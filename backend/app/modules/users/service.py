# backend/app/modules/users/service.py
import string
import random
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from beanie import PydanticObjectId
from beanie.operators import In

from app.modules.users.models import User, UserRole
# Assuming AppSetting is also migrated to Beanie
from app.modules.settings.models import AppSetting
# Assuming other models are migrated
from app.modules.shops.models import Shop
from app.core.enums import MasterPipelineStage, GlobalTaskStatus
from app.modules.timetable.models import TimetableEvent
from app.modules.meetings.models import MeetingSummary

class UserService:
    def __init__(self):
        # No db session needed in Beanie!
        pass

    async def generate_referral_code(self, user_id: PydanticObjectId) -> Optional[str]:
        user = await User.get(user_id)
        if not user:
            return None
        
        if user.referral_code:
            return user.referral_code
        
        # Generate a unique referral code: SETU-ROLE-RANDOM
        prefix = "SETU"
        role_part = user.role[:3].upper() if user.role else "USR"
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        code = f"{prefix}-{role_part}-{random_part}"
        
        # Ensure uniqueness
        while await User.find_one(User.referral_code == code):
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            code = f"{prefix}-{role_part}-{random_part}"
            
        user.referral_code = code
        await user.save() # Replaces db.commit() and db.refresh()
        return code

    async def get_user_by_referral(self, code: str) -> Optional[User]:
        return await User.find_one(User.referral_code == code)

    async def get_next_employee_code(self) -> tuple[Optional[str], Optional[int]]:
        """Generate the next sequential employee code based on settings."""
        
        prefix_row = await AppSetting.find_one(AppSetting.key == "emp_code_prefix")
        seq_row = await AppSetting.find_one(AppSetting.key == "emp_code_next_seq")
        enabled_row = await AppSetting.find_one(AppSetting.key == "emp_code_enabled")
        
        enabled = enabled_row.value.lower() == "true" if enabled_row else True
        if not enabled:
            return None, None

        prefix = prefix_row.value if prefix_row else "EMP"
        seq = int(seq_row.value) if seq_row else 1
        
        code = f"{prefix}{seq:03d}"
        
        # Ensure uniqueness
        while await User.find_one(User.employee_code == code):
            seq += 1
            code = f"{prefix}{seq:03d}"
            
        return code, seq

    async def increment_employee_code_seq(self, current_seq: int):
        """Increment the sequence in settings."""
        seq_row = await AppSetting.find_one(AppSetting.key == "emp_code_next_seq")
        if seq_row:
            seq_row.value = str(current_seq + 1)
            await seq_row.save()
        else:
            new_setting = AppSetting(key="emp_code_next_seq", value=str(current_seq + 1))
            await new_setting.insert()

    async def get_employee_code_settings(self) -> Dict[str, Any]:
        """Fetch current employee code settings."""
        prefix_row = await AppSetting.find_one(AppSetting.key == "emp_code_prefix")
        seq_row = await AppSetting.find_one(AppSetting.key == "emp_code_next_seq")
        enabled_row = await AppSetting.find_one(AppSetting.key == "emp_code_enabled")
        
        return {
            "enabled": enabled_row.value.lower() == "true" if enabled_row else True,
            "prefix": prefix_row.value if prefix_row else "EMP",
            "next_seq": int(seq_row.value) if seq_row else 1
        }

    async def update_employee_code_settings(self, enabled: bool, prefix: str, next_seq: int) -> Dict[str, Any]:
        """Update employee code settings."""
        settings_data = [
            ("emp_code_enabled", str(enabled).lower()),
            ("emp_code_prefix", prefix),
            ("emp_code_next_seq", str(next_seq))
        ]
        
        for key, val in settings_data:
            row = await AppSetting.find_one(AppSetting.key == key)
            if row:
                row.value = val
                await row.save()
            else:
                new_setting = AppSetting(key=key, value=val)
                await new_setting.insert()
                
        return {"enabled": enabled, "prefix": prefix, "next_seq": next_seq}

    async def suggest_pm(self) -> Optional[Dict[str, Any]]:
        pm_roles = [UserRole.PROJECT_MANAGER, UserRole.PROJECT_MANAGER_AND_SALES]
        active_stages = [MasterPipelineStage.NEGOTIATION, MasterPipelineStage.MAINTENANCE]
        
        # Beanie In operator for checking lists
        pms = await User.find(
            In(User.role, pm_roles),
            User.is_active == True,
            User.is_deleted == False
        ).to_list()
        
        if not pms:
            return None
            
        best_pm = None
        lowest_workload = float('inf')
        
        for pm in pms:
            # Count operations in Beanie
            workload = await Shop.find(
                Shop.project_manager_id == pm.id,
                In(Shop.pipeline_stage, active_stages),
                Shop.is_deleted == False
            ).count()
            
            if workload < lowest_workload:
                lowest_workload = workload
                best_pm = pm
                
        if best_pm:
            return {
                "user_id": str(best_pm.id),
                "name": best_pm.name,
                "workload": lowest_workload
            }
        return None

    async def get_user_availability(self, user_id: PydanticObjectId, target_date: date) -> Optional[Dict[str, Any]]:
        user = await User.get(user_id)
        if not user:
            return None

        booked_hours = set()

        # 1. Timetable Events
        # We need to construct datetime objects to query properly if your TimetableEvent uses dates
        target_start = datetime.combine(target_date, datetime.min.time())
        target_end = datetime.combine(target_date, datetime.max.time())

        events = await TimetableEvent.find(
            TimetableEvent.user_id == user_id,
            TimetableEvent.date >= target_start,
            TimetableEvent.date <= target_end,
            TimetableEvent.is_deleted == False
        ).to_list()
        
        for e in events:
            if e.start_time:
                start_h = e.start_time.hour
                end_h = e.end_time.hour if e.end_time else start_h + 1
                for h in range(start_h, end_h):
                    booked_hours.add(h)

        # 2. Meetings (Host or Attendee)
        # Note how simple this is compared to the SQL join!
        meetings = await MeetingSummary.find(
            MeetingSummary.date >= target_start,
            MeetingSummary.date <= target_end,
            In(MeetingSummary.status, [GlobalTaskStatus.OPEN, GlobalTaskStatus.IN_PROGRESS]),
            MeetingSummary.is_deleted == False
        ).to_list()
        
        # Filter in Python for complex OR logic (Host OR Attendee)
        user_meetings = [
            m for m in meetings 
            if m.host_id == user_id or (m.attendee_ids and user_id in m.attendee_ids)
        ]
        
        for m in user_meetings:
            if m.date:
                booked_hours.add(m.date.hour)

        slots = []
        for h in range(10, 19): # 10 AM to 6 PM
            time_str = f"{h if h <= 12 else h - 12}:00 {'AM' if h < 12 else 'PM'}"
            slots.append({
                "time": time_str,
                "hour24": h,
                "is_available": h not in booked_hours
            })

        return {
            "user_id": str(user_id),
            "name": user.name or user.email,
            "date": target_date.isoformat(),
            "slots": slots
        }

    async def get_group_availability(self, user_ids: List[PydanticObjectId], target_date: date) -> Optional[Dict[str, Any]]:
        if not user_ids:
            return None
        
        all_avail = []
        for uid in user_ids:
            avail = await self.get_user_availability(uid, target_date)
            if avail:
                all_avail.append(avail)
        
        if not all_avail:
            return None
        
        common_slots = []
        for i in range(len(all_avail[0]["slots"])):
            base_slot = all_avail[0]["slots"][i]
            hour = base_slot["hour24"]
            
            is_common_free = True
            for user_data in all_avail:
                if not user_data["slots"][i]["is_available"]:
                    is_common_free = False
                    break
            
            common_slots.append({
                "time": base_slot["time"],
                "hour24": hour,
                "is_available": is_common_free
            })
            
        return {
            "user_ids": [str(uid) for uid in user_ids],
            "date": target_date.isoformat(),
            "slots": common_slots
        }

    async def get_pm_availability(self, pm_id: PydanticObjectId, target_date: date) -> Optional[Dict[str, Any]]:
        base = await self.get_user_availability(pm_id, target_date)
        if not base:
            return None
        
        booked_hours = {s["hour24"] for s in base["slots"] if not s["is_available"]}

        target_start = datetime.combine(target_date, datetime.min.time())
        target_end = datetime.combine(target_date, datetime.max.time())

        shops_with_demos = await Shop.find(
            Shop.project_manager_id == pm_id,
            Shop.demo_scheduled_at >= target_start,
            Shop.demo_scheduled_at <= target_end,
            Shop.is_deleted == False
        ).to_list()
        
        for shop in shops_with_demos:
            if shop.demo_scheduled_at:
                booked_hours.add(shop.demo_scheduled_at.hour)
        
        for s in base["slots"]:
            s["is_available"] = s["hour24"] not in booked_hours
            
        return base
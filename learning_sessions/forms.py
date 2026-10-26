from django import forms
from django.utils import timezone

from exchanges.models import SkillExchange
from .models import LearningSession


class LearningSessionForm(forms.ModelForm):
    exchange = forms.ModelChoiceField(
        queryset=SkillExchange.objects.none(),
        label="Accepted skill exchange",
        empty_label="Choose an exchange"
    )

    class Meta:
        model = LearningSession
        fields = [
            "exchange",
            "session_date",
            "start_time",
            "end_time",
            "meeting_link",
            "notes",
            "reminder_enabled",
        ]

        widgets = {
            "session_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "start_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "meeting_link": forms.URLInput(
                attrs={
                    "placeholder": "https://meet.google.com/..."
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "What will you learn in this session?"
                }
            ),
            "reminder_enabled": forms.CheckboxInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        if user is not None:
            self.fields["exchange"].queryset = (
                SkillExchange.objects.filter(
                    status="accepted"
                ).filter(
                    # Include exchanges where this user participates.
                    requester=user
                )
                | SkillExchange.objects.filter(
                    status="accepted",
                    receiver=user
                )
            ).distinct()

    def clean_session_date(self):
        session_date = self.cleaned_data["session_date"]

        if session_date < timezone.localdate():
            raise forms.ValidationError(
                "You cannot schedule a session in the past."
            )

        return session_date

    def clean(self):
        cleaned_data = super().clean()

        session_date = cleaned_data.get("session_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        exchange = cleaned_data.get("exchange")

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "end_time",
                "End time must be later than start time."
            )

        if session_date and start_time:
            session_datetime = timezone.make_aware(
                timezone.datetime.combine(
                    session_date, start_time
                )
            )

            if session_datetime <= timezone.now():
                self.add_error(
                    "start_time",
                    "Choose a start time in the future."
                )

        if exchange and self.user:
            if (
                exchange.requester_id != self.user.id
                and exchange.receiver_id != self.user.id
            ):
                self.add_error(
                    "exchange",
                    "You must be a participant in this exchange."
                )

        return cleaned_data
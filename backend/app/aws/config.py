from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    R2_ACCESS_KEY: str | None = None
    R2_SECRET_KEY: str | None = None
    R2_BUCKET_NAME: str | None = None
    R2_ACCOUNT_ID: str | None = None


aws_settings = AWSSettings()  # type: ignore[call-arg]

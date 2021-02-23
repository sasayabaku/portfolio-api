# Qiita Worker
Qiitaの情報を収集するAPI

## Deploy to App Engine

### Set `app.yaml`
```yaml
runtime: python38
instance_class: F1

env_variables:
  QIITA_TOKEN: '<Qiita APIのトークン>'
```

### deploy

```bash
gcloud app deploy --bucket=gs://<任意のCloud Storage>
```

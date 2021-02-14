# portfolio-api
Heroku portfolio api / data collect worker

## Setup

### Enviornment Value
```bash
export GOOGLE_APPLICATIONS_CREDENTIALS=/path/google/cedential.json

export QIITA_TOKEN=/value/qiita/token
```

## Collect qiita value + upload firestore

```bash
python -m worker
```
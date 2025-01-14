## SETUP GUIDE

### 1. train model (if no existing is available)
`rasa train`

### 2. provide keys (for custom actions)
ensure both `MONGODB_KEY` & `OPENAI_KEY` files have their respective required strings available

### 3. run actions server (in new terminal)
`rasa run actions --debug`

### 4. run rasa shell
`rasa shell`

## DEPENDENCIES
1. `python version = 3.10`
2. `pip install rasa`

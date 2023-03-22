## Hacking

```bash
pip3 install pdm
# build and install ng_ai
pdm install
# run unit tests
pdm run test
# run integration tests
pdm run int-test
# lint
pdm run lint
# format
pdm run format

# integration tests environment setup
pdm run dockerup
pdm run dockerdown
pdm run dockerstatus

# integration tests environment teardown
pdm run teardown
```
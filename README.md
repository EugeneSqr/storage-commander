## storage-commander
Unified way of managing files in various remote storages.

### installation
Clone the repository:
```bash
git clone https://github.com/EugeneSqr/storage-commander.git
cd storage-commander
```

Install it with pipx:
```bash
pipx install .
```

Alternatively install with pip even though it's [no longer recommended](https://peps.python.org/pep-0668/):
```bash
pip install .
```

Copy the `.storcom-complete.bash` from the root of the cloned project repository to `~/.config/storcom`, then source it in bash:
```bash
. "$HOME/.config/storcom/.storcom-complete.bash"
```
To make this change permanent, add the line above to your `.bashrc`.

### development setup
Clone the repository:
```bash
git clone https://github.com/EugeneSqr/storage-commander.git
cd storage-commander
```

Create virtual environment and activate it:
```bash
python -m venv env
. env/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Install the app:
```bash
pip install --editable .
```

### configuration
The configuration for all supported storages resides in a single file `~/.config/storcom/config.toml`.

It should look something like this:
```toml
[dev.fcc]
storage_url = "http://localhost:8000"
[dev.fcc.tokens]
service1 = "xxx"

[qa.cx]
storage_url = "http://qa-api-carrierx.int"
[qa.cx.tokens]
service2 = "yyy"

[shortcuts]
feature_X_on_dev = "dev:fcc:service1:container1"
feature_Y_on_qa = "qa:cx:service2:container2"
```

Each file location is defined by 4 parameters:
1. environment - dev, staging, prod etc.
2. storage - FCC, CX, Amazon S3 (not supported yet) etc.
3. service - can be called partner, namespace, domain depending on the storage
4. user - think about it as a container

A combination of these parameters is called a __context__.

The configuration above defines two distinct storages __fcc__ and __cx__ in two environments __dev__ and __qa__ with tokens for two users __user1__ and __user2__. The __shortcuts__ section contains short meaningful names for __contexts__. The main purpose of shortcuts is to ease switching between the __contexts__.

### usage
Each command is executed within a __context__. Immediately after the installation the context is empty:
```bash
storcom context show
{'environment': '', 'storage': '', 'service': '', 'user': ''}
```

There are two main ways of setting/changing the context:
1. Specify each context parameter individually:
```bash
storcom context use --environment=dev --storage=fcc --service=service1 --user=container1
{'environment': 'dev', 'storage': 'fcc', 'service': 'service1', 'user': 'container1'}
```
2. Use a __shortcut__ specified in the `config.toml`:
```bash
$ storcom context use feature_Y_on_qa
{'environment': 'qa', 'storage': 'cx', 'service': 'service2', 'user': 'container2'}
```

The context is preserved across app runs in the `~/.config/storcom/.context` text file.

After the context is set the app is ready to work with files. Here are some examples:
1. List all files in a tabular fashion:
```bash
storcom file ll
 file_sid                             | name                         | type   | mime_type                   | date_modified
--------------------------------------+------------------------------+--------+-----------------------------+--------------------------
 972ee129-54de-462b-94c3-f42611bf3a6e | 1104-13075222214.vp8         | file   | application/octet-stream    | 2023-01-18T09:36:22.643Z
 e7288d7f-bf89-458f-89de-9f5b9aa87fcb | 1104-13075222214.g722        | audio  | audio/G722                  | 2023-01-18T09:36:22.671Z
```
2. Show file details by its ID (piped to jq for clarity). The result HTTP request's curl representation is optionally printed to stderr with `--show_curl`:
``` bash
storcom file --show_curl show 972ee129-54de-462b-94c3-f42611bf3a6e | jq
curl -X GET -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' -H 'Authorization: Bearer yyy' -H 'Connection: keep-alive' -H 'User-Agent: python-requests/2.31.0' http://qa-api-carrierx.int/core/v2/storage/files/container2
{
  "file_sid": "972ee129-54de-462b-94c3-f42611bf3a6e",
  "partner_sid": "service2",
  "container_sid": "container2",
  "parent_file_sid": null,
  "name": "1104-13075222214.vp8",
  "type": "file",
  "unique": false,
  "file_bytes": 12,
  "file_access_name": "972ee129-54de-462b-94c3-f42611bf3a6e.vp8",
  "publish": "file_sid",
  "publish_uri": "...",
  "lifecycle_ttl": -1,
  "lifecycle_action": "no_action",
  "date_modified": "2023-01-18T09:36:22.643Z",
  "desired_format": null,
  "desired_bitrate": null,
  "mime_type": "application/octet-stream",
  "content_format": "vp8",
  "content_duration": null,
  "content_transcoding_progress": null,
  "threshold_include": true,
  "date_last_accessed": null,
  "content_classification": "unknown"
}
```
3. Remove all files:
```bash
storcom file ls | jq -r '.items[].file_sid' | xargs storcom file rm
```

We first list all files as JSON. Then parse the output and extract the ids. We finally use `xargs` to feed the extracted ids to `storcom file rm`.

4. Remove files from storage B which ids present in storage A:
```bash
storcom file --context_string=feature_Y_on_qa ls | jq -r '.items[].file_sid' | xargs storcom file --context_string=feature_X_on_dev rm
```

Note how __context__ gets changed on the fly.

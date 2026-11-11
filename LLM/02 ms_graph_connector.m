# Microsoft Graph Python SDK — Complete SharePoint Connector Guide

## 1. What are we learning?

The Microsoft Graph Python SDK (`msgraph-sdk`) lets Python applications communicate with Microsoft 365 services.

For this lesson, we'll use it to connect to SharePoint and:

1. Authenticate with Microsoft.
2. Connect to a SharePoint document library.
3. List files and folders.
4. Read file metadata.
5. Navigate folders.
6. Find a document by name.
7. Download a document.
8. Handle errors and understand pagination.

### How the connection works

Python application → `msgraph-sdk` → Microsoft Graph API → SharePoint.

Microsoft Graph is the API. The Python SDK is the library that makes calling that API easier.

A SharePoint document library is represented by a **Drive**. A file or folder inside it is represented by a **DriveItem**.

---

# 2. Install the required packages

Run:

```bash
pip install msgraph-sdk azure-identity python-dotenv
```

What these packages do:

| Package | Purpose |
|---|---|
| `msgraph-sdk` | Microsoft Graph API client |
| `azure-identity` | Authentication and access tokens |
| `python-dotenv` | Loads credentials from a `.env` file |

The SDK uses asynchronous requests, so we'll use Python's `async` and `await`.

---

# 3. Register your application in Microsoft Entra ID

Microsoft needs to know which application is trying to access SharePoint.

You need an App Registration.

1. Open https://entra.microsoft.com/
2. Go to **App registrations**.
3. Select **New registration**.
4. Give your application a name, for example `PythonSharePointConnector`.
5. Register it.
6. Copy the following values:
   - Directory (tenant) ID
   - Application (client) ID
7. Open **Certificates & secrets**.
8. Create a client secret and copy its value immediately.
9. Open **API permissions**.
10. Add Microsoft Graph application permissions.

For this example, use:

`Files.Read.All`

This allows the application to read files across the organisation's accessible drives and is a broad permission. An administrator must grant consent.

For a production application, consider `Sites.Selected` and grant access only to the required SharePoint sites. The administrator must configure the appropriate site-level permission as well.

Important: never put your client secret directly into Python code or commit it to Git.

---

# 4. Create your project

Project structure:

```text
sharepoint_connector/
│
├── connector.py
├── .env
├── .gitignore
└── downloads/
```

Create a `.env` file:

```env
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
DRIVE_ID=your-sharepoint-drive-id

DOWNLOAD_DIR=downloads
```

Create a `.gitignore` file:

```text
.env
.venv/
__pycache__/
downloads/
```

The Drive ID identifies the SharePoint document library you want to access. It is not the same as the Site ID or an individual file ID.

---

# 5. Complete Python connector — one script

Save this as `connector.py`.

```python
import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient


# ==========================================================
# 1. LOAD CONFIGURATION
# ==========================================================

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
DRIVE_ID = os.getenv("DRIVE_ID")

DOWNLOAD_DIR = Path(
    os.getenv("DOWNLOAD_DIR", "downloads")
)

required_values = {
    "TENANT_ID": TENANT_ID,
    "CLIENT_ID": CLIENT_ID,
    "CLIENT_SECRET": CLIENT_SECRET,
    "DRIVE_ID": DRIVE_ID,
}

missing = [
    name
    for name, value in required_values.items()
    if not value
]

if missing:
    raise ValueError(
        f"Missing environment variables: {missing}"
    )


# ==========================================================
# 2. AUTHENTICATION
# ==========================================================

credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

SCOPES = [
    "https://graph.microsoft.com/.default"
]


# ==========================================================
# 3. CREATE GRAPH CLIENT
# ==========================================================

client = GraphServiceClient(
    credentials=credential,
    scopes=SCOPES
)


# ==========================================================
# 4. LIST FILES AND FOLDERS
# ==========================================================

async def list_folder(
    drive_id: str,
    folder_id: str = "root"
):
    """
    List files and folders inside a SharePoint folder.

    drive_id:
        Identifies the document library.

    folder_id:
        Identifies the folder.
        Use 'root' for the library's root folder.
    """

    result = await (
        client.drives
        .by_drive_id(drive_id)
        .items
        .by_drive_item_id(folder_id)
        .children
        .get()
    )

    items = []

    if result and result.value:

        for item in result.value:

            is_folder = item.folder is not None
            is_file = item.file is not None

            item_info = {
                "name": item.name,
                "id": item.id,
                "size": item.size,
                "is_folder": is_folder,
                "is_file": is_file,
                "web_url": item.web_url,
                "created": item.created_date_time,
                "modified": item.last_modified_date_time,
                "mime_type": (
                    item.file.mime_type
                    if is_file
                    else None
                ),
            }

            items.append(item_info)

            print("\n--------------------------")
            print("Name:", item_info["name"])
            print("ID:", item_info["id"])
            print("Size:", item_info["size"])
            print("Folder:", item_info["is_folder"])
            print("File:", item_info["is_file"])
            print("URL:", item_info["web_url"])
            print("Modified:", item_info["modified"])
            print("MIME type:", item_info["mime_type"])

    else:
        print("No items found.")

    return items


# ==========================================================
# 5. GET DETAILS OF ONE ITEM
# ==========================================================

async def get_item(
    drive_id: str,
    item_id: str
):
    """
    Retrieve metadata for one file or folder.
    """

    item = await (
        client.drives
        .by_drive_id(drive_id)
        .items
        .by_drive_item_id(item_id)
        .get()
    )

    if item is None:
        return None

    print("Name:", item.name)
    print("ID:", item.id)
    print("Size:", item.size)
    print("Web URL:", item.web_url)
    print("Created:", item.created_date_time)
    print("Modified:", item.last_modified_date_time)

    return item


# ==========================================================
# 6. FIND A FILE BY NAME
# ==========================================================

async def find_file(
    drive_id: str,
    folder_id: str,
    target_filename: str
):
    """
    Find a file by exact name in one folder.

    This checks only the folder supplied.
    It does not automatically search subfolders.
    """

    items = await list_folder(
        drive_id=drive_id,
        folder_id=folder_id
    )

    for item in items:

        if (
            item["name"] == target_filename
            and item["is_file"]
        ):
            print("File found:", target_filename)
            return item

    print("File not found:", target_filename)

    return None


# ==========================================================
# 7. DOWNLOAD A FILE
# ==========================================================

async def download_file(
    drive_id: str,
    file_id: str,
    filename: str
):
    """
    Download a file using its DriveItem ID.
    """

    DOWNLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Use only the filename, not an untrusted path
    safe_filename = Path(filename).name

    output_path = DOWNLOAD_DIR / safe_filename

    content = await (
        client.drives
        .by_drive_id(drive_id)
        .items
        .by_drive_item_id(file_id)
        .content
        .get()
    )

    if content is None:
        raise RuntimeError(
            "No file content returned."
        )

    with open(output_path, "wb") as file:
        file.write(content)

    print("Downloaded:", output_path)

    return output_path


# ==========================================================
# 8. MAIN PROGRAM
# ==========================================================

async def main():

    try:

        # List items in the document library root
        items = await list_folder(
            drive_id=DRIVE_ID,
            folder_id="root"
        )

        # Example: find a document
        target = "Employee_Handbook.pdf"

        matching_file = next(
            (
                item for item in items
                if item["name"] == target
                and item["is_file"]
            ),
            None
        )

        # Download it if found
        if matching_file:

            await download_file(
                drive_id=DRIVE_ID,
                file_id=matching_file["id"],
                filename=matching_file["name"]
            )

        else:
            print(
                f"{target} was not found in the root folder."
            )

    finally:

        # Close the asynchronous credential
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python connector.py
```

The download operation expects the content endpoint to return the file bytes. For very large files, use a streaming/download approach rather than keeping the entire document in memory.

---

# 6. Understand every important component

## A. `load_dotenv()`

```python
load_dotenv()
```

**What:** Loads values from `.env` into environment variables.

**Why:** We don't want credentials hardcoded in our source code.

**How:**

```python
TENANT_ID = os.getenv("TENANT_ID")
```

This reads the value named `TENANT_ID`.

Useful functions:

| Function | Meaning |
|---|---|
| `load_dotenv()` | Load `.env` |
| `os.getenv("NAME")` | Read an environment variable |
| `os.environ["NAME"]` | Read a required variable; raises an error if absent |
| `Path("downloads")` | Represent a filesystem path |

Use `os.getenv()` when you want to handle missing values yourself.

## B. `ClientSecretCredential`

```python
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
```

This comes from `azure.identity.aio`.

It authenticates the application using its client ID and client secret.

### Parameters

| Parameter | Meaning | Why it matters |
|---|---|---|
| `tenant_id` | Organisation ID | Identifies the Microsoft Entra tenant |
| `client_id` | Application ID | Identifies your registered application |
| `client_secret` | Application password | Proves the application's identity |

### What is a tenant?

A tenant is an organisation's Microsoft identity environment.

For example, a company may have its own Microsoft 365 tenant containing employees, groups, SharePoint sites and applications.

### What is a client ID?

Every registered application has an identifier.

Microsoft uses it to identify which application is making the request.

### What is a client secret?

It is a credential used by your application to authenticate.

It must be protected like a password.

### What happens after authentication?

The credential obtains an access token from Microsoft Entra ID.

The Graph SDK uses that token when making API requests.

You normally don't need to manually request a token for every API call. The credential handles token acquisition and caching.

## C. `SCOPES`

```python
SCOPES = [
    "https://graph.microsoft.com/.default"
]
```

**What:** Defines the resource and permission scope requested during authentication.

**Why:** Microsoft Graph needs to know which resource the access token is intended for.

For application authentication, `.default` tells Microsoft to use the application permissions configured and consented to for that application.

Important: `.default` does not grant every permission automatically. Your application still needs the correct API permissions and administrator consent.

## D. `GraphServiceClient`

```python
client = GraphServiceClient(
    credentials=credential,
    scopes=SCOPES
)
```

This is the main object you'll use throughout your project.

### Parameters

| Parameter | Meaning |
|---|---|
| `credentials` | Authentication object |
| `scopes` | Requested resource scopes |

The client provides access to different Microsoft Graph resources.

Examples:

```python
client.drives
client.sites
client.users
client.groups
client.me
client.device_management
```

These represent different Graph API resource areas. Access depends on the permissions granted to your application.

For SharePoint documents, we'll mainly use `client.drives` and sometimes `client.sites`.

---

# 7. Understand the SharePoint object hierarchy

The most important part of learning this SDK is understanding the object navigation.

Consider:

```python
client.drives.by_drive_id(DRIVE_ID)
```

This selects a document library.

Then:

```python
.items
```

Accesses the items in that drive.

Then:

```python
.by_drive_item_id("root")
```

Selects the root folder.

Then:

```python
.children
```

Selects the items inside that folder.

Finally:

```python
.get()
```

Sends a GET request.

The whole expression:

```python
result = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .items
    .by_drive_item_id("root")
    .children
    .get()
)
```

is equivalent to the Graph REST API request:

```http
GET /drives/{drive-id}/items/root/children
```

### Meaning of each method and property

| Expression | Meaning |
|---|---|
| `client` | Main Graph client |
| `.drives` | Access drives |
| `.by_drive_id(id)` | Select a drive |
| `.items` | Access drive items |
| `.by_drive_item_id(id)` | Select a particular item |
| `.children` | Access items inside a folder |
| `.get()` | Perform a GET request |
| `await` | Wait for the asynchronous response |

The SDK uses method chaining to build the request.

---

# 8. Understand the returned `DriveItem` attributes

When you list a folder, Microsoft Graph returns a collection of `DriveItem` objects.

Each item can represent a file or folder.

The following are useful attributes.

| Attribute | What it means | Typical use |
|---|---|---|
| `item.id` | Unique item ID | Download or retrieve the item |
| `item.name` | File/folder name | Identify documents |
| `item.size` | Size in bytes | File size checks |
| `item.web_url` | Browser URL | Open document in SharePoint |
| `item.created_date_time` | Creation timestamp | Track when created |
| `item.last_modified_date_time` | Modification timestamp | Detect changes |
| `item.file` | File-specific properties | Check if it is a file |
| `item.folder` | Folder-specific properties | Check if it is a folder |
| `item.parent_reference` | Parent location information | Understand folder hierarchy |
| `item.created_by` | Creator information | Audit and ownership |
| `item.last_modified_by` | Last editor information | Track changes |
| `item.e_tag` | Version-related entity tag | Change detection |
| `item.c_tag` | Content-related entity tag | Content change tracking |
| `item.description` | Description, if available | Metadata |
| `item.shared` | Sharing information, if available | Sharing context |
| `item.file_system_info` | File system timestamps | File metadata |

Not every property is guaranteed to be populated in every response.

### How to check whether an item is a file or folder

```python
if item.folder is not None:
    print("This is a folder")

if item.file is not None:
    print("This is a file")
```

Why?

A DriveItem is a common object representing both files and folders.

Graph uses different properties to describe the type.

### File-specific attributes

```python
item.file.mime_type
item.file.hashes
```

`mime_type` tells you the file format.

Examples:

| File | MIME type |
|---|---|
| PDF | `application/pdf` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| TXT | `text/plain` |

`hashes` may contain file hashes, such as SHA-1 or QuickXorHash, when available.

Use hashes to help detect duplicate content or verify content identity. Don't assume every hash is available.

### Folder-specific attributes

```python
item.folder.child_count
```

This tells you how many direct children the folder contains, when provided.

Example:

```python
if item.folder:
    print("Children:", item.folder.child_count)
```

This is useful when deciding whether a folder is worth exploring.

---

# 9. Common SharePoint connector operations

## A. Get the document library details

```python
drive = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .get()
)

print(drive.id)
print(drive.name)
print(drive.drive_type)
print(drive.web_url)
```

Useful Drive attributes:

| Attribute | Meaning |
|---|---|
| `drive.id` | Drive ID |
| `drive.name` | Library name |
| `drive.drive_type` | Type of drive |
| `drive.web_url` | Browser URL |
| `drive.description` | Description, if available |
| `drive.owner` | Owner information, if available |
| `drive.quota` | Storage quota information, if available |

Use this when you want to verify that you connected to the correct library.

## B. List root folder contents

```python
result = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .items
    .by_drive_item_id("root")
    .children
    .get()
)

for item in result.value:
    print(item.name)
```

Use `"root"` to access the document library's root folder.

## C. List a particular folder

```python
FOLDER_ID = "your-folder-id"

result = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .items
    .by_drive_item_id(FOLDER_ID)
    .children
    .get()
)
```

Use a folder's ID when you want to navigate into it.

## D. Get one particular file

```python
FILE_ID = "your-file-id"

item = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .items
    .by_drive_item_id(FILE_ID)
    .get()
)

print(item.name)
print(item.size)
print(item.web_url)
```

This retrieves metadata about the selected file.

## E. Download a file

```python
content = await (
    client.drives
    .by_drive_id(DRIVE_ID)
    .items
    .by_drive_item_id(FILE_ID)
    .content
    .get()
)

with open("document.pdf", "wb") as f:
    f.write(content)
```

Important:

- `.content` accesses the file-content endpoint.
- `.get()` retrieves the file data.
- `"wb"` opens the local file in binary write mode.
- `f.write(content)` writes the bytes to disk.

Use binary mode because PDFs, DOCX files and XLSX files are binary formats.

---

# 10. Understand query parameters

Graph API supports query parameters that control what data is returned.

These are important when retrieving large document libraries.

The main parameters include:

| Parameter | Meaning | Why use it |
|---|---|---|
| `$select` | Choose properties to return | Reduce unnecessary metadata |
| `$top` | Request a page size | Control number of returned items |
| `$orderby` | Sort results | Order by name or modification time |
| `$filter` | Filter results | Retrieve matching records where supported |
| `$expand` | Include related resources | Retrieve additional related data |
| `$skiptoken` | Continue pagination | Retrieve subsequent pages |

Example Graph REST request:

```http
GET /drives/{drive-id}/items/{folder-id}/children?$select=id,name,size,file,folder,lastModifiedDateTime&$top=50
```

This asks for up to 50 items and selects only the specified fields.

Why use `$select`?

Imagine a library contains thousands of documents. You may only need the file name, ID, size and modified date.

Requesting unnecessary metadata wastes bandwidth and makes responses larger.

The SDK provides request configuration and query-parameter classes for passing these options. Their generated Python import paths and available options depend on the SDK version. Check the installed version's generated request-builder classes rather than assuming a class name from another language's SDK.

Also, not every Graph endpoint supports every query option. Check the endpoint documentation before relying on `$filter` or `$orderby`.

---

# 11. Pagination — a very important concept

Suppose a SharePoint folder contains 1,000 documents.

Graph does not necessarily return all 1,000 in one response.

Instead, it returns a page and may provide an `@odata.nextLink`.

Example response:

```json
{
  "value": [
    {
      "id": "file001",
      "name": "document1.pdf"
    }
  ],
  "@odata.nextLink": "https://graph.microsoft.com/..."
}
```

The next link tells your application where to continue.

Why pagination matters:

If you only process the first response, you may miss hundreds of documents.

The SDK's collection response exposes the next-link information as a generated model property, commonly `odata_next_link`.

For production, use the SDK's page iterator or follow the next-link URL using the SDK request adapter. Do not construct a new URL by manually guessing the continuation token.

Also, don't assume that setting `$top` guarantees the entire collection is returned.

---

# 12. Recursive folder navigation

A document library can have nested folders:

```text
Company Documents/
│
├── HR/
│   ├── Policies/
│   │   ├── Leave.pdf
│   │   └── Benefits.pdf
│   │
│   └── Employee_Handbook.pdf
│
├── Finance/
│   ├── Annual_Report.xlsx
│   └── Budget.pdf
│
└── Legal/
    └── Contracts/
```

Listing the root only returns its direct children.

To inspect nested folders, you must list their children as well.

A recursive function can do this:

```python
async def walk_folder(drive_id, folder_id="root"):

    items = await list_folder(
        drive_id,
        folder_id
    )

    for item in items:

        if item["is_folder"]:

            await walk_folder(
                drive_id,
                item["id"]
            )

        elif item["is_file"]:

            print("Found file:", item["name"])
```

This explores folders inside folders.

Production considerations:

- Handle pagination in every folder.
- Limit concurrent requests.
- Handle access-denied folders.
- Avoid revisiting the same item.
- Handle deleted or moved folders.
- Apply sensible recursion limits if needed.

---

# 13. Common errors

| Error | Likely cause | What to check |
|---|---|---|
| `401 Unauthorized` | Invalid or missing authentication | Tenant, client ID and secret |
| `403 Forbidden` | Insufficient permissions | Graph permissions and admin consent |
| `404 Not Found` | Incorrect drive or item ID | Confirm IDs |
| `429 Too Many Requests` | Request throttling | Respect `Retry-After` |
| `500` or `503` | Microsoft service issue | Retry with backoff |
| Empty result | Folder is empty or wrong location | Confirm drive and folder IDs |

Do not automatically retry every error.

For example, a 403 permission error normally requires fixing permissions, not repeatedly sending the same request.

For 429 and temporary 5xx errors, implement retries with exponential backoff and respect the server's `Retry-After` header.

---

# 14. Important security considerations

1. Keep secrets in environment variables or a managed secret store.
2. Use the minimum permissions needed.
3. Prefer site-specific permissions where practical.
4. Respect SharePoint access restrictions.
5. Don't expose access tokens in logs.
6. Protect downloaded documents.
7. Avoid logging confidential document content.
8. Rotate credentials and consider certificate-based authentication for production applications.

---

# 15. Quick reference: important SDK expressions

| Expression | What it does |
|---|---|
| `GraphServiceClient(...)` | Creates the Graph client |
| `client.drives` | Accesses document libraries and drives |
| `client.sites` | Accesses SharePoint sites |
| `.by_drive_id(id)` | Selects a drive |
| `.by_drive_item_id(id)` | Selects a file or folder |
| `.items` | Accesses drive items |
| `.children` | Accesses folder contents |
| `.root` | Accesses drive root |
| `.content` | Accesses file content |
| `.get()` | Retrieves data |
| `.post()` | Creates data where supported |
| `.patch()` | Updates data where supported |
| `.delete()` | Deletes data where supported |
| `result.value` | Collection of returned objects |
| `item.id` | Item identifier |
| `item.name` | Item name |
| `item.size` | Item size |
| `item.file` | File properties |
| `item.folder` | Folder properties |
| `item.web_url` | Browser URL |

Remember: the SDK is generated from Graph's API description. Available methods and request configuration options depend on the resource and SDK version.

---

# 16. Official documentation

- Microsoft Graph Python SDK: https://github.com/microsoftgraph/msgraph-sdk-python
- Python SDK drive examples: https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/drives_samples.md
- List folder contents: https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0
- Download DriveItem content: https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0
- Microsoft Graph permissions reference: https://learn.microsoft.com/en-us/graph/permissions-reference
- Azure Identity Python documentation: https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme

---

# 17. What you should be able to do after this lesson

- Explain what Microsoft Graph is.
- Explain the difference between a Drive, DriveItem, file and folder.
- Authenticate an application using `ClientSecretCredential`.
- Create a `GraphServiceClient`.
- List SharePoint files.
- Read file metadata.
- Retrieve a file by its ID.
- Download a file.
- Understand pagination and API permissions.
- Explain the difference between an API request and the Python SDK method that sends it.

**Practical exercise:** Connect to a test SharePoint document library, list its root folder, identify a PDF, retrieve its metadata and download it.


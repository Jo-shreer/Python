# Complete Lesson: Connecting Python to SharePoint Using Microsoft Graph REST API and `requests`

## 1. What are we building?

We are building a Python connector that communicates with SharePoint through Microsoft Graph API.

Our eventual architecture is:

**SharePoint → Microsoft Graph API → Python (`requests`) → Amazon S3 (`boto3`)**

For this lesson, we will concentrate on the first part: connecting to SharePoint and retrieving its files.

By the end, you will understand how to:
1. Authenticate with Microsoft Graph.
2. Connect to a SharePoint document library.
3. Retrieve its files and folders.
4. Understand the API response.
5. Extract file information.
6. Handle pagination.
7. Handle common API errors.

---

# 2. What is Microsoft Graph API?

Microsoft Graph API is Microsoft's REST API for accessing Microsoft 365 services.

For example, it allows Python applications to communicate with:

- SharePoint
- OneDrive
- Outlook
- Microsoft Teams
- Users and groups
- Microsoft 365 files and documents

Instead of manually opening SharePoint in a browser, we can use Python to send an HTTP request to Microsoft Graph.

Microsoft Graph receives the request, checks authentication and permissions, and returns the requested information.

### Example

Imagine your SharePoint document library contains:

```text
Company Documents
│
├── Financial Report.pdf
├── Employee Handbook.docx
├── Sales Data.xlsx
└── Technical Documentation.pdf
```

We want Python to retrieve the names and IDs of these files.

We can do that using:

```python
requests.get(url, headers=headers)
```

This sends an HTTP GET request to Microsoft Graph.

---

# 3. What is REST API?

REST stands for Representational State Transfer.

A REST API allows applications to communicate with each other using HTTP requests.

The most common HTTP methods are:

| Method | Purpose | Example |
|---|---|---|
| GET | Retrieve information | Get SharePoint files |
| POST | Create information or trigger an operation | Create a folder |
| PUT | Replace a resource | Replace file content |
| PATCH | Update selected properties | Rename a file |
| DELETE | Delete a resource | Delete a file |

In our current lesson, we use **GET** because we want to retrieve information from SharePoint.

We are not uploading, changing or deleting anything.

---

# 4. What is the `requests` library?

`requests` is a Python library used to send HTTP requests.

It allows Python to communicate with external APIs.

### Why do we use it?

Microsoft Graph exposes REST API endpoints.

The `requests` library allows us to call those endpoints directly without using the Microsoft Graph SDK.

### Installation

Run this in your terminal:

```bash
pip install requests
```

### Import

```python
import requests
```

Explanation:

| Component | Explanation |
|---|---|
| `import` | Python instruction to load a module |
| `requests` | Name of the library |
| `requests.get()` | Method that sends an HTTP GET request |

You can use the library without creating a separate Graph SDK client.

---

# 5. Understanding authentication

Before accessing SharePoint, Microsoft needs to know:

1. Which application is making the request?
2. Is the application authenticated?
3. Does it have permission to access the requested SharePoint content?

This is where an **access token** comes in.

## What is an access token?

An access token is a temporary credential issued by Microsoft Entra ID.

It proves that the application has authenticated and identifies the permissions granted to it.

Think of it as a temporary access pass.

Our Python application sends this token with its API request.

### Example

```python
access_token = "YOUR_ACCESS_TOKEN"
```

Explanation:

| Component | Meaning |
|---|---|
| `access_token` | Variable storing the token |
| `=` | Assignment operator |
| `"YOUR_ACCESS_TOKEN"` | Placeholder for the actual token |

This is not a real token. You must obtain one through Microsoft Entra ID authentication.

### Where does the token come from?

Typically, you need:

- Microsoft Entra tenant ID
- Application (client) ID
- Client secret or certificate, depending on authentication method
- Appropriate Microsoft Graph permissions

For an unattended enterprise connector, application authentication using client credentials is common.

The token is obtained from the Microsoft identity platform's token endpoint.

For Microsoft Graph, the application commonly requests this scope:

```text
https://graph.microsoft.com/.default
```

This means Microsoft should issue a token containing the Graph application permissions that have been configured and consented to for that application.

### Important permissions

For example:

- `Files.Read.All`: read files the application is permitted to access under this permission.
- `Sites.Read.All`: read SharePoint site content covered by this permission.
- `Sites.Selected`: access only SharePoint sites for which the application has been explicitly granted access.

These permissions are not interchangeable. The correct permission depends on the endpoint and the access model.

Use the least privilege necessary. An administrator may need to grant consent, and `Sites.Selected` also requires a separate site-level permission grant.

**Important:** Do not put a real access token or client secret directly into production source code.

---

# 6. Understanding the SharePoint identifiers

Our code uses two important identifiers:

```python
site_id = "YOUR_SITE_ID"
drive_id = "YOUR_DRIVE_ID"
```

Let's understand them.

## What is a site ID?

A site ID identifies a SharePoint site.

For example:

```text
https://company.sharepoint.com/sites/Finance
```

This represents a SharePoint site.

The Graph API identifies the site using its site ID.

## What is a drive ID?

A drive ID identifies a document library or OneDrive drive.

For example:

```text
Finance SharePoint Site
│
├── Documents
├── Shared Documents
└── Reports
```

Each document library has its own drive ID.

In Microsoft Graph terminology:

- A `site` represents a SharePoint site.
- A `drive` represents a document library or OneDrive.
- A `driveItem` represents an individual file or folder.

### Why do we need a drive ID?

Because our API request needs to know which document library to retrieve files from.

For example:

```python
drive_id = "YOUR_DRIVE_ID"
```

If the company has several document libraries, each may have a different drive ID.

### Do we need both site ID and drive ID?

Not for the particular endpoint we are using.

Our current endpoint is:

```text
/drives/{drive_id}/root/children
```

It only requires the drive ID.

We can use the site ID in other endpoints to discover sites and their document libraries.

---

# 7. Understanding the API URL

This is the most important part of our code:

```python
url = (
    f"https://graph.microsoft.com/v1.0/"
    f"drives/{drive_id}/root/children"
)
```

Let's break it down.

## Part 1: `https://graph.microsoft.com`

This is the Microsoft Graph API base URL.

It tells Python where to send the HTTP request.

## Part 2: `/v1.0`

This specifies the Microsoft Graph API version.

Microsoft Graph has different API versions.

| Version | Meaning |
|---|---|
| `v1.0` | Generally available API |
| `beta` | Preview API; behaviour can change |

For production applications, prefer `v1.0` when the endpoint supports the functionality you need.

## Part 3: `/drives/`

This tells Graph that we want to work with a drive.

A drive represents a document library or OneDrive.

## Part 4: `{drive_id}`

This is the unique identifier of the document library.

Python inserts the value of our `drive_id` variable into the URL.

## Part 5: `/root`

This identifies the root folder of the document library.

For example:

```text
Documents
│
├── Report.pdf
├── Budget.xlsx
└── Policies
```

The root is the top-level folder called `Documents` in this example.

## Part 6: `/children`

This asks Microsoft Graph to return the immediate children of the root folder.

These can be files or folders.

### Complete example URL

Assume our drive ID is `abc123`.

The resulting URL would look like:

```text
https://graph.microsoft.com/v1.0/drives/abc123/root/children
```

This means:

"Microsoft Graph, retrieve the files and folders immediately inside the root folder of drive abc123."

---

# 8. What is an f-string?

Our URL contains:

```python
f"drives/{drive_id}/root/children"
```

The `f` before the quotation marks makes this an f-string.

An f-string allows us to insert Python variables into text.

Example:

```python
company = "ABC"

message = f"Welcome to {company}"

print(message)
```

Output:

```text
Welcome to ABC
```

In our connector:

```python
drive_id = "abc123"

url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
```

Output:

```text
https://graph.microsoft.com/v1.0/drives/abc123/root/children
```

Without the `f`, Python would treat `{drive_id}` as ordinary text.

---

# 9. Understanding HTTP headers

Our code contains:

```python
headers = {
    "Authorization": f"Bearer {access_token}"
}
```

Headers provide additional information about an HTTP request.

They tell the API things such as:

- Who is making the request?
- What authentication credential should be checked?
- What response format is acceptable?

Let's break this down.

## What is a dictionary?

In Python, a dictionary stores information as key-value pairs.

Example:

```python
person = {
    "name": "John",
    "department": "Finance"
}
```

Here:

- `name` is a key.
- `John` is its value.
- `department` is another key.
- `Finance` is its value.

Our `headers` variable is also a dictionary.

## What is Authorization?

```python
"Authorization"
```

This is an HTTP header name.

It tells Microsoft Graph that the request includes authentication information.

## What is Bearer?

```python
"Bearer"
```

Bearer is the authentication scheme used to send the access token.

It is followed by a space and then the token.

For example:

```text
Authorization: Bearer eyJhbGciOi...
```

The actual token is much longer.

## Why do we need this header?

Without the appropriate authentication information, Microsoft Graph will generally reject the request.

You might receive:

```text
401 Unauthorized
```

This usually means the token is missing, invalid, expired or intended for the wrong resource.

---

# 10. Sending the API request

Now we reach the actual connection:

```python
response = requests.get(url, headers=headers)
```

Let's understand every component.

## `requests`

The imported Python library.

## `.get()`

A method provided by the requests library.

It sends an HTTP GET request.

## `url`

The API endpoint we want to contact.

## `headers=headers`

This passes our authentication headers to the API.

The first `headers` is the parameter name expected by `requests.get()`.

The second `headers` is our Python dictionary.

## `response`

This variable stores the HTTP response returned by Microsoft Graph.

It is a Python `Response` object.

It is not yet the extracted JSON dictionary.

### What happens behind the scenes?

1. Python sends an HTTP GET request.
2. The request goes to Microsoft Graph.
3. Microsoft checks the access token.
4. Microsoft checks the application's permissions.
5. Microsoft identifies the requested drive and root folder.
6. Microsoft retrieves the immediate children.
7. Microsoft returns an HTTP response.
8. Python stores that response in `response`.

---

# 11. Understanding the Response object

After the API call, we can inspect the response.

For example:

```python
print(response.status_code)
print(response.headers)
print(response.text)
```

### A. `response.status_code`

Returns the HTTP status code.

Common examples:

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 400 | Invalid request |
| 401 | Authentication failed |
| 403 | Access forbidden |
| 404 | Resource not found |
| 429 | Too many requests |
| 500 | Server error |
| 503 | Service temporarily unavailable |

For our GET request, `200` normally means success.

Example output:

```text
200
```

### B. `response.headers`

Returns the HTTP response headers.

These are different from the request headers we sent.

Response headers can include information about content type, request IDs and throttling.

### C. `response.text`

Returns the response body as text.

For example:

```text
{"value":[{"name":"Financial Report.pdf","id":"file123"}]}
```

This is JSON text.

---

# 12. Understanding JSON

JSON stands for JavaScript Object Notation.

It is a common format used by APIs to exchange information.

Microsoft Graph usually returns JSON when we request file metadata.

Example response:

```json
{
    "value": [
        {
            "name": "Financial Report.pdf",
            "id": "file123",
            "size": 204800
        },
        {
            "name": "Employee Handbook.docx",
            "id": "file456",
            "size": 102400
        }
    ]
}
```

Let's understand the structure.

## Outer object

```json
{
    "value": []
}
```

The response is a JSON object.

`value` is a property containing an array of results.

## Array

```json
[
    {
        "name": "Financial Report.pdf"
    },
    {
        "name": "Employee Handbook.docx"
    }
]
```

An array is a collection of items.

In Python, JSON arrays become lists.

## Individual objects

```json
{
    "name": "Financial Report.pdf",
    "id": "file123"
}
```

Each file is represented by an object.

In Python, JSON objects become dictionaries.

---

# 13. Converting JSON into Python data

Our code uses:

```python
files = response.json()
```

Let's understand this carefully.

## What is `.json()`?

`.json()` is a method of the requests `Response` object.

It parses the response body as JSON and converts it into Python data structures.

The conversion is:

| JSON type | Python type |
|---|---|
| Object `{}` | Dictionary `dict` |
| Array `[]` | List `list` |
| String | `str` |
| Number | `int` or `float` |
| `true` | `True` |
| `false` | `False` |
| `null` | `None` |

For example:

JSON:

```json
{
    "name": "Financial Report.pdf",
    "size": 204800
}
```

Python:

```python
{
    "name": "Financial Report.pdf",
    "size": 204800
}
```

The result is now a Python dictionary.

### Why do we need `.json()`?

Because we want to work with the returned file information using Python.

We can access individual properties, loop through files and pass information to other systems.

---

# 14. Understanding the `value` attribute

Our next code is:

```python
files["value"]
```

Why `value`?

Because Microsoft Graph places collection results inside the `value` property.

For our request, this contains the files and folders returned from the document library.

Example:

```python
files = {
    "value": [
        {
            "name": "Financial Report.pdf",
            "id": "file123"
        },
        {
            "name": "Employee Handbook.docx",
            "id": "file456"
        }
    ]
}
```

To retrieve the list:

```python
file_list = files["value"]
```

Output:

```python
[
    {
        "name": "Financial Report.pdf",
        "id": "file123"
    },
    {
        "name": "Employee Handbook.docx",
        "id": "file456"
    }
]
```

### What does `["value"]` mean?

It accesses the dictionary entry whose key is `value`.

This is dictionary indexing.

It is not a special Microsoft Graph function.

It is normal Python.

---

# 15. Understanding the for loop

Our code:

```python
for file in files["value"]:
    print(file["name"])
```

Let's break it down.

## `for`

A Python keyword used to repeat an operation for each item in a collection.

## `file`

A variable representing the current item in the loop.

You could call it something else:

```python
for item in files["value"]:
    print(item["name"])
```

Both versions work.

## `in`

Tells Python which collection to iterate over.

## `files["value"]`

The list containing the returned file and folder objects.

## `:`

The colon marks the beginning of the loop body.

## Indentation

The indented line belongs to the loop.

## `print()`

Displays information in the terminal.

### How does the loop work?

Suppose Graph returns three items:

```python
[
    {"name": "Report.pdf"},
    {"name": "Budget.xlsx"},
    {"name": "Policies"}
]
```

Python processes them one at a time.

First iteration:

```python
file = {"name": "Report.pdf"}
```

Second iteration:

```python
file = {"name": "Budget.xlsx"}
```

Third iteration:

```python
file = {"name": "Policies"}
```

The print statement runs once for each item.

Expected output:

```text
Report.pdf
Budget.xlsx
Policies
```

Notice that `Policies` may be a folder, not a file. The `/children` endpoint returns both files and folders.

---

# 16. Understanding file attributes

Each SharePoint file or folder is represented by a Microsoft Graph `driveItem`.

A driveItem can contain many properties.

Here are some important ones.

| Attribute | What it tells us |
|---|---|
| `id` | Unique ID of the file or folder within its drive |
| `name` | File or folder name |
| `size` | Size in bytes |
| `webUrl` | Browser URL for the item |
| `createdDateTime` | Creation date and time |
| `lastModifiedDateTime` | Last modification date and time |
| `eTag` | Version-related identifier for the item |
| `cTag` | Content version-related identifier, when available |
| `parentReference` | Information about the parent location |
| `file` | File-specific information, when the item is a file |
| `folder` | Folder-specific information, when the item is a folder |

Example:

```json
{
    "id": "file123",
    "name": "Financial Report.pdf",
    "size": 204800,
    "webUrl": "https://company.sharepoint.com/...",
    "createdDateTime": "2026-10-10T09:00:00Z",
    "lastModifiedDateTime": "2026-11-01T12:30:00Z",
    "file": {
        "mimeType": "application/pdf"
    }
}
```

### How do we access these attributes in Python?

```python
for file in files["value"]:

    print(file["id"])
    print(file["name"])
    print(file["size"])
    print(file["webUrl"])
```

Expected output:

```text
file123
Financial Report.pdf
204800
https://company.sharepoint.com/...
```

### Important: `file` versus `folder`

A driveItem may have a `file` property or a `folder` property.

For example:

File:

```json
{
    "name": "Report.pdf",
    "file": {
        "mimeType": "application/pdf"
    }
}
```

Folder:

```json
{
    "name": "Finance",
    "folder": {
        "childCount": 12
    }
}
```

To distinguish between them:

```python
for item in files["value"]:

    if "file" in item:
        print(item["name"], "is a file")

    elif "folder" in item:
        print(item["name"], "is a folder")
```

Expected output:

```text
Report.pdf is a file
Finance is a folder
```

This distinction becomes important when we build a connector that downloads documents but also needs to explore nested folders.

---

# 17. Complete improved version of our connector

Now let's put everything together.

This version includes:

- Authentication header
- API URL
- Request timeout
- HTTP error handling
- JSON parsing
- File and folder identification
- Important metadata
- Pagination

```python
import requests

# STEP 1: Authentication token
access_token = "YOUR_ACCESS_TOKEN"

# STEP 2: SharePoint document library ID
drive_id = "YOUR_DRIVE_ID"

# STEP 3: Create authentication headers
headers = {
    "Authorization": f"Bearer {access_token}"
}

# STEP 4: Create API URL
url = (
    f"https://graph.microsoft.com/v1.0/"
    f"drives/{drive_id}/root/children"
)

# STEP 5: Send request and process all pages
while url:

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    # STEP 6: Check for HTTP errors
    response.raise_for_status()

    # STEP 7: Convert JSON response into Python dictionary
    data = response.json()

    # STEP 8: Process each returned item
    for item in data.get("value", []):

        print("--------------------------------")

        print("Name:", item.get("name"))
        print("ID:", item.get("id"))
        print("Size:", item.get("size"))
        print("Web URL:", item.get("webUrl"))

        if "file" in item:
            print("Type: File")
            print(
                "MIME Type:",
                item["file"].get("mimeType")
            )

        elif "folder" in item:
            print("Type: Folder")
            print(
                "Child Count:",
                item["folder"].get("childCount")
            )

        print(
            "Last Modified:",
            item.get("lastModifiedDateTime")
        )

    # STEP 9: Get the next page URL, if one exists
    url = data.get("@odata.nextLink")

print("SharePoint listing completed.")
```

---

# 18. Explanation of every additional parameter and method

## A. `timeout=30`

This is a parameter passed to `requests.get()`.

It tells requests how long to wait for the server before raising a timeout exception.

Here, `30` means 30 seconds.

Why use it?

Without a timeout, a request can wait much longer than intended if the server or network stops responding.

Example:

```python
response = requests.get(
    url,
    headers=headers,
    timeout=30
)
```

The timeout can also be specified as a pair:

```python
timeout=(5, 30)
```

This means:

- 5 seconds for establishing the connection.
- 30 seconds for waiting for the response data.

These are not necessarily strict total-operation deadlines.

## B. `raise_for_status()`

```python
response.raise_for_status()
```

This method checks whether the HTTP response indicates an unsuccessful request.

If the status is successful, execution continues.

If the status is an HTTP error, requests raises an exception.

For example:

```text
403 Client Error: Forbidden
```

Why use it?

Because without checking the status, your program might attempt to process an error response as though it contained the requested file information.

## C. `data.get("value", [])`

```python
data.get("value", [])
```

This uses Python's dictionary `.get()` method.

It tries to retrieve the value associated with the key `value`.

The second argument, `[]`, is the default value.

Meaning:

- If `value` exists, return its contents.
- If `value` does not exist, return an empty list.

Compare:

```python
data["value"]
```

with:

```python
data.get("value", [])
```

The first can raise a `KeyError` if the key is missing.

The second returns an empty list instead.

## D. `item.get("name")`

This retrieves the `name` property from the current item.

If it is missing, it returns `None` by default.

You can also specify a custom default:

```python
item.get("name", "Unknown")
```

## E. `@odata.nextLink`

This is a Microsoft Graph pagination property.

Graph may not return every item in a single response.

Instead, it returns a page of results and provides a URL for the next page.

For example:

```json
{
    "value": [
        {
            "name": "Report1.pdf"
        },
        {
            "name": "Report2.pdf"
        }
    ],
    "@odata.nextLink": "https://graph.microsoft.com/v1.0/..."
}
```

Our code uses:

```python
url = data.get("@odata.nextLink")
```

If another page exists, `url` becomes the next-page URL.

If no next page exists, `url` becomes `None`.

Then the `while url:` loop stops.

### What is `while`?

`while` repeats a block of code as long as its condition is true.

In our case:

```python
while url:
```

means:

"Keep retrieving pages while a next-page URL is available."

This is essential when a SharePoint library contains many files.

---

# 19. Example output

Assume our SharePoint document library contains:

```text
Financial Report.pdf
Employee Handbook.docx
Finance
```

An illustrative terminal output could be:

```text
--------------------------------
Name: Financial Report.pdf
ID: file123
Size: 204800
Web URL: https://company.sharepoint.com/...
Type: File
MIME Type: application/pdf
Last Modified: 2026-11-01T12:30:00Z

--------------------------------
Name: Employee Handbook.docx
ID: file456
Size: 102400
Web URL: https://company.sharepoint.com/...
Type: File
MIME Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Last Modified: 2026-11-02T10:00:00Z

--------------------------------
Name: Finance
ID: folder789
Size: 0
Web URL: https://company.sharepoint.com/...
Type: Folder
Child Count: 12
Last Modified: 2026-11-03T08:30:00Z

SharePoint listing completed.
```

These are example values, not actual results from your SharePoint environment.

---

# 20. What happens if something goes wrong?

| Error | Possible cause | What to check |
|---|---|---|
| 400 Bad Request | Incorrect URL or request parameters | Check the endpoint and identifiers |
| 401 Unauthorized | Invalid or expired token | Obtain a valid access token |
| 403 Forbidden | Insufficient permissions | Check Graph permissions and site access |
| 404 Not Found | Incorrect drive ID or resource | Verify the drive ID |
| 429 Too Many Requests | Microsoft Graph throttling | Respect `Retry-After` and retry |
| 500 Internal Server Error | Microsoft service error | Retry appropriately |
| 503 Service Unavailable | Temporary service issue | Retry with backoff |
| Timeout | Network or service delay | Check connectivity and timeout settings |

A production connector should implement controlled retries for temporary failures.

For `429` responses, Microsoft Graph can provide a `Retry-After` response header. Follow that guidance instead of repeatedly sending requests immediately.

---

# 21. Important limitations of our current code

Our current code retrieves only the immediate children of the root folder.

For example:

```text
Documents
│
├── Report.pdf
├── Budget.xlsx
└── Finance
    │
    ├── January.xlsx
    └── February.xlsx
```

Our current endpoint:

```text
/drives/{drive_id}/root/children
```

returns:

- `Report.pdf`
- `Budget.xlsx`
- `Finance`

It does not automatically return:

- `January.xlsx`
- `February.xlsx`

To retrieve nested documents, we must explore the folder structure recursively or request the children of each folder.

Also, retrieving a file's metadata is not the same as downloading its contents.

For example:

```python
item["name"]
```

gives us its name.

It does not give us the PDF or Word document bytes.

To download a file, we will use a separate Graph endpoint:

```text
GET /drives/{drive_id}/items/{item_id}/content
```

That is the next step in our connector.

---

# 22. What have we achieved?

We have built the first part of an enterprise source connector.

| Stage | Status |
|---|---|
| Import requests | Completed |
| Supply access token | Required |
| Identify document library | Required |
| Construct Graph API URL | Completed |
| Send authenticated GET request | Completed |
| Receive HTTP response | Completed |
| Parse JSON | Completed |
| Extract file metadata | Completed |
| Identify files and folders | Completed |
| Handle pagination | Completed |
| Download actual document contents | Next step |
| Upload documents to Amazon S3 | Later step |

## Key concepts to remember

1. `requests` is the Python library that sends HTTP requests.
2. `access_token` authenticates the application.
3. `drive_id` identifies the document library.
4. `headers` carries authentication information.
5. `url` identifies the API endpoint.
6. `requests.get()` sends the request.
7. `response` stores the HTTP response.
8. `response.raise_for_status()` checks for HTTP errors.
9. `response.json()` converts JSON into Python objects.
10. `data["value"]` accesses the collection of returned items.
11. `for item in ...` processes each item.
12. `item["name"]` retrieves the item's name.
13. `@odata.nextLink` allows us to retrieve subsequent pages.

**The most important distinction:** listing a SharePoint document tells us that a file exists and gives us its metadata. Downloading the actual file content is a separate operation.

Our next lesson should be downloading one PDF from SharePoint using `requests`, understanding the `/content` endpoint, the response bytes, and then uploading those bytes to Amazon S3 using `boto3`.

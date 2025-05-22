# 🚀 OpoTimeAPI – API Dokumentation

**Base URL:** `https://opotimeapi.onrender.com`

Alle Endpunkte benötigen (sofern nicht anders angegeben) einen JWT `access` Token im Header:

```http
Authorization: Bearer <access_token>
```

---

## ✉️ Registrierung

**POST** `/register/`

Erstellt einen neuen Benutzer.

**Body Parameter:**

| Name     | Typ    | Pflicht | Beschreibung             |
| -------- | ------ | ------- | ------------------------ |
| username | string | ja      | Gewünschter Benutzername |
| email    | string | ja      | E-Mail-Adresse           |
| password | string | ja      | Passwort                 |

**Beispiel:**

```json
POST /register/
{
  "username": "aileen",
  "email": "aileen@example.com",
  "password": "supergeheim123"
}
```

---

## 🔐 Login

**POST** `/login/`

Authentifiziert den Benutzer mit Username **oder** E-Mail + Passwort.

**Body Parameter:**

| Name     | Typ    | Pflicht | Beschreibung         |
| -------- | ------ | ------- | -------------------- |
| username | string | ja      | Username oder E-Mail |
| password | string | ja      | Passwort             |

**Beispiel:**

```json
POST /login/
{
  "username": "aileen@example.com",
  "password": "supergeheim123"
}
```

**Antwort:** Access- und Refresh-Token.

---

## ♻️ Token erneuern

**POST** `/refresh/`

Erneuert das `access` Token mithilfe des `refresh` Tokens.

**Body Parameter:**

| Name    | Typ    | Pflicht | Beschreibung           |
| ------- | ------ | ------- | ---------------------- |
| refresh | string | ja      | Gültiger Refresh-Token |

---

## 🕰️ Zeiteinträge

**Endpoint:** `/time/`

### GET

Listet Zeiteinträge ab einem bestimmten Datum, optional gefiltert.

**Query Parameter:**

| Name        | Typ    | Pflicht | Beschreibung                                 |
| ----------- | ------ | ------- | -------------------------------------------- |
| since       | string | ja      | Startdatum (ISO, z. B. 2024-05-01T00:00:00Z) |
| project\_id | int    | nein    | Filter nach Projekt-ID                       |
| user\_id    | int    | nein    | Filter nach User-ID                          |

**Beispiel:**

```
GET /time/?since=2024-05-01T00:00:00Z&project_id=1
```

### POST

Erstellt einen neuen Zeiteintrag.

```json
POST /time/
{
  "project": 1,
  "type": "start"
}
```

### PATCH

```json
PATCH /time/
{
  "entry_id": 5,
  "type": "end"
}
```

### DELETE

```
DELETE /time/?entry_id=5
```

---

## 📄 Projekte

**Endpoint:** `/projects/`

### GET

* Alle eigenen & eingeladenen Projekte
* Optional nach ID oder Name filtern

**Query Parameter:**

| Name          | Typ    | Pflicht | Beschreibung            |
| ------------- | ------ | ------- | ----------------------- |
| project\_id   | int    | nein    | Konkretes Projekt holen |
| project\_name | string | nein    | Nach Namen filtern      |

### POST

```json
{
  "name": "Mein neues Projekt"
}
```

### PATCH

```json
{
  "project_id": 3,
  "name": "Neuer Projektname"
}
```

### DELETE

```
DELETE /projects/?project_id=3
```

---

## 📋 Aufgaben

**Endpoint:** `/tasks/`

### GET

* Alle Aufgaben oder nach Projekt oder ID filtern

**Query Parameter:**

| Name        | Typ | Pflicht | Beschreibung            |
| ----------- | --- | ------- | ----------------------- |
| project\_id | int | nein    | Aufgaben eines Projekts |
| task\_id    | int | nein    | Eine konkrete Aufgabe   |

### POST

```json
{
  "project": 1,
  "assigned_to": 2,
  "text": "Frontend bauen",
  "status": "new"
}
```

### PATCH

```json
{
  "task_id": 4,
  "status": "done",
  "text": "API finalisiert"
}
```

### DELETE

```
DELETE /tasks/?task_id=4
```

---

## 📥 Einladungen

**Endpoint:** `/invitations/`

### GET

Listet Einladungen eines Projekts, optional nur akzeptierte.

**Query Parameter:**

| Name        | Typ    | Pflicht | Beschreibung             |
| ----------- | ------ | ------- | ------------------------ |
| project\_id | int    | ja      | Projekt-ID               |
| accepted    | string | nein    | "true" = nur angenommene |

### POST

```json
{
  "project": 2,
  "to_user": 7
}
```

### PATCH

```json
{
  "invitation_id": 3,
  "status": "accepted"
}
```

---

## 🔍 Benutzersuche

**GET** `/user-search/`

Findet Benutzer anhand von Teilstring in Username oder E-Mail.

**Query Parameter:**

| Name | Typ    | Pflicht | Beschreibung             |
| ---- | ------ | ------- | ------------------------ |
| q    | string | ja      | Suchbegriff z. B. "test" |

**Beispiel:**

```
GET /user-search/?q=test
```

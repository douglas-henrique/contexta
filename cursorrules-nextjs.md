# Contexta Next.js Frontend - Cursor Rules

You are working on the **Next.js frontend** for Contexta, a professional RAG (Retrieval-Augmented Generation) SaaS platform.

## PROJECT OVERVIEW

**Contexta** is a multi-tenant RAG platform where users can:
- Upload documents (PDF, TXT, DOCX)
- Ask questions about their documents
- Get AI-powered answers with source citations
- Manage their document library

**Tech Stack:**
- Frontend: Next.js 14+ (App Router)
- Backend: Django REST API + FastAPI (RAG Engine)
- Authentication: JWT tokens
- Styling: Tailwind CSS (recommended)
- State Management: React Context / Zustand / TanStack Query

---

## BACKEND API DOCUMENTATION

### Base URLs
```
Django Backend: http://localhost:8000
FastAPI Query API: http://localhost:8002
```

---

## 🔐 AUTHENTICATION API

**Base URL:** `http://localhost:8000/api/auth/`

All authentication endpoints use JSON and return JWT tokens.

### 1. Register User
```http
POST /api/auth/register/
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}
```

**Success Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-08T12:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Access Token Lifetime:** 60 minutes  
**Refresh Token Lifetime:** 7 days

---

### 2. Login
```http
POST /api/auth/login/
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-08T12:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials."
}
```

---

### 3. Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Logout
```http
POST /api/auth/logout/
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200):**
```json
{
  "message": "Logout successful."
}
```

---

### 5. Get Current User Profile
```http
GET /api/auth/me/
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-08T12:00:00Z"
}
```

---

### 6. Update User Profile
```http
PATCH /api/auth/me/
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body (partial update):**
```json
{
  "first_name": "John",
  "last_name": "Smith"
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "date_joined": "2024-01-08T12:00:00Z"
}
```

---

### 7. Change Password
```http
POST /api/auth/change-password/
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "string",
  "new_password": "string",
  "new_password_confirm": "string"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully."
}
```

---

## 📄 DOCUMENTS API

**Base URL:** `http://localhost:8000/api/documents/`

All endpoints require authentication (JWT Bearer token).

### 1. List Documents
```http
GET /api/documents/
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "title": "My Document",
    "file": "http://localhost:8000/media/documents/file.pdf",
    "status": "completed",
    "created_at": "2024-01-08T12:00:00Z",
    "updated_at": "2024-01-08T12:05:00Z",
    "owner": 1
  }
]
```

**Document Status Values:**
- `pending` - Waiting to be processed
- `processing` - Currently being ingested
- `completed` - Successfully processed and indexed
- `failed` - Processing failed

---

### 2. Get Single Document
```http
GET /api/documents/{id}/
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "id": 1,
  "title": "My Document",
  "file": "http://localhost:8000/media/documents/file.pdf",
  "status": "completed",
  "created_at": "2024-01-08T12:00:00Z",
  "updated_at": "2024-01-08T12:05:00Z",
  "owner": 1
}
```

---

### 3. Upload Document
```http
POST /api/documents/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (form-data):**
- `title` (string, required): Document title
- `file` (file, required): PDF, TXT, or DOCX file

**Success Response (201):**
```json
{
  "id": 1,
  "title": "My Document",
  "file": "http://localhost:8000/media/documents/file.pdf",
  "status": "pending",
  "created_at": "2024-01-08T12:00:00Z",
  "updated_at": "2024-01-08T12:00:00Z",
  "owner": 1
}
```

**Notes:**
- Document automatically triggers ingestion pipeline
- Status will change from `pending` → `processing` → `completed`
- Check status periodically or implement polling/websockets

---

### 4. Delete Document
```http
DELETE /api/documents/{id}/
Authorization: Bearer {access_token}
```

**Success Response (204):**
No content

---

## 🤖 QUERY API (RAG)

**Base URL:** `http://localhost:8002`

This is the FastAPI service for querying documents using RAG.

### 1. Query Documents
```http
POST /query
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What is the main topic of my documents?",
  "tenant_id": 1,
  "top_k": 10,
  "rerank_top_k": 5,
  "max_context_length": 3000
}
```

**Parameters:**
- `query` (string, required): User's question
- `tenant_id` (integer, required): User ID from Django (for multi-tenancy)
- `top_k` (integer, optional, default=10): Number of chunks to retrieve
- `rerank_top_k` (integer, optional, default=5): Number of chunks after re-ranking
- `max_context_length` (integer, optional, default=3000): Max characters for context

**Success Response (200):**
```json
{
  "answer": "Based on your documents, the main topic is...",
  "sources": [
    {
      "document_id": 1,
      "chunk_index": 0,
      "score": 0.95,
      "text_preview": "This is a preview of the relevant text..."
    }
  ],
  "query": "What is the main topic of my documents?",
  "tenant_id": 1
}
```

**Notes:**
- Use the authenticated user's ID as `tenant_id`
- This ensures users only query their own documents
- RAG pipeline: embedding → vector search → re-ranking → LLM generation

---

## 🏗️ NEXT.JS BEST PRACTICES

### Authentication Flow

**1. Store JWT Tokens Securely:**

**Option A: HTTP-Only Cookies (Recommended for production)**
- More secure (XSS protection)
- Requires backend CORS configuration
- Use `credentials: 'include'` in fetch

**Option B: localStorage (Simpler for development)**
```typescript
// After login/register
localStorage.setItem('accessToken', tokens.access);
localStorage.setItem('refreshToken', tokens.refresh);

// On app load
const accessToken = localStorage.getItem('accessToken');
```

---

**2. Create Auth Context:**
```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  
  // Implementation here
  
  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

---

**3. Create API Client:**
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const accessToken = localStorage.getItem('accessToken');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  // Handle token refresh if 401
  if (response.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      // Retry request with new token
      return apiFetch(endpoint, options);
    } else {
      // Redirect to login
      window.location.href = '/login';
    }
  }
  
  return response;
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) return false;
  
  try {
    const response = await fetch(`${API_URL}/api/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    });
    
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('accessToken', data.access);
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
  
  return false;
}
```

---

**4. Protected Routes:**
```typescript
// middleware.ts (Next.js 14+)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('accessToken');
  
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/documents/:path*'],
};
```

---

### File Upload Example

```typescript
// components/DocumentUpload.tsx
async function handleUpload(file: File, title: string) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  
  const response = await apiFetch('/api/documents/', {
    method: 'POST',
    body: formData,
    headers: {
      // Don't set Content-Type, browser will set it with boundary
    },
  });
  
  if (response.ok) {
    const document = await response.json();
    console.log('Document uploaded:', document);
    // Poll for status updates
    pollDocumentStatus(document.id);
  }
}

function pollDocumentStatus(documentId: number) {
  const interval = setInterval(async () => {
    const response = await apiFetch(`/api/documents/${documentId}/`);
    const document = await response.json();
    
    if (document.status === 'completed' || document.status === 'failed') {
      clearInterval(interval);
      // Update UI
    }
  }, 2000); // Check every 2 seconds
}
```

---

### Query Documents Example

```typescript
// components/Chat.tsx
async function askQuestion(question: string, userId: number) {
  const response = await fetch('http://localhost:8002/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: question,
      tenant_id: userId,
      top_k: 10,
      rerank_top_k: 5,
    }),
  });
  
  const data = await response.json();
  return data; // { answer, sources, query, tenant_id }
}
```

---

## 🎨 UI/UX RECOMMENDATIONS

### Pages Structure
```
/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   ├── documents/
│   │   ├── chat/
│   │   └── layout.tsx
│   └── layout.tsx
```

### Key Features
1. **Authentication Pages:** Login, Register, Password Reset
2. **Dashboard:** Overview of documents and recent queries
3. **Document Management:** Upload, list, delete documents with status indicators
4. **Chat Interface:** Ask questions with streaming responses
5. **Profile Settings:** Update profile, change password

---

## ⚙️ ENVIRONMENT VARIABLES

Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_QUERY_API_URL=http://localhost:8002
```

---

## 🔒 SECURITY BEST PRACTICES

1. **Never expose tokens in URLs or logs**
2. **Implement auto token refresh before expiration**
3. **Use HTTPS in production**
4. **Validate user input before sending to API**
5. **Handle API errors gracefully**
6. **Implement rate limiting on client side**
7. **Clear tokens on logout**

---

## 🚀 RECOMMENDED LIBRARIES

```bash
npm install @tanstack/react-query  # API state management
npm install zustand                 # Global state
npm install react-hook-form         # Form handling
npm install zod                     # Schema validation
npm install axios                   # HTTP client (alternative to fetch)
npm install date-fns               # Date formatting
```

---

## 📝 CODING STANDARDS

- Use TypeScript for type safety
- Use Server Components when possible (Next.js 14+)
- Use Client Components for interactivity
- Implement proper error boundaries
- Add loading states for async operations
- Use optimistic updates for better UX
- Follow Next.js App Router conventions
- Use Tailwind CSS for styling
- Keep components small and focused
- Write unit tests for critical logic

---

## 🎯 MULTI-TENANCY

**Critical:** Always use the authenticated user's ID as `tenant_id` in all API calls to the Query API. This ensures data isolation between users.

```typescript
const user = useAuth();
const response = await fetch('http://localhost:8002/query', {
  method: 'POST',
  body: JSON.stringify({
    query: question,
    tenant_id: user.id, // ← Always use authenticated user's ID
  }),
});
```

---

## 🐛 COMMON ISSUES & SOLUTIONS

### CORS Errors
- Ensure Django CORS settings include your Next.js URL
- Check that `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`

### 401 Unauthorized
- Check if access token is expired (60 min lifetime)
- Implement token refresh logic
- Verify Bearer token format: `Authorization: Bearer {token}`

### Document Upload Fails
- Check file size limits
- Verify file type (PDF, TXT, DOCX only)
- Ensure multipart/form-data content type

### Query Returns No Results
- Verify documents are in "completed" status
- Check tenant_id matches user ID
- Ensure documents have been ingested successfully

---

## 📚 ADDITIONAL RESOURCES

- [Next.js Documentation](https://nextjs.org/docs)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://jwt.io/introduction)
- [React Query](https://tanstack.com/query/latest)

---

**Remember:** This is a professional, production-grade application. Write clean, maintainable code with proper error handling, loading states, and user feedback. Test thoroughly before deploying.

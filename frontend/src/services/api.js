import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Fetch paginated list of students, optionally filtered by enrollment status.
 */
export function getStudents(page = 1, perPage = 10, enrollmentStatus = '') {
  const params = { page, per_page: perPage }
  if (enrollmentStatus) {
    params.enrollment_status = enrollmentStatus
  }
  return apiClient.get('/students', { params })
}

/**
 * Fetch a single student by ID.
 */
export function getStudent(id) {
  return apiClient.get(`/students/${id}`)
}

/**
 * Create a new student.
 */
export function createStudent(data) {
  return apiClient.post('/students', data)
}

/**
 * Update an existing student (full replacement).
 */
export function updateStudent(id, data) {
  return apiClient.put(`/students/${id}`, data)
}

/**
 * Delete a student by ID.
 */
export function deleteStudent(id) {
  return apiClient.delete(`/students/${id}`)
}

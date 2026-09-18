<script setup>
import { ref, watch } from 'vue'
import { getStudents, deleteStudent } from '@/services/api'

const emit = defineEmits(['edit'])

const students = ref([])
const loading = ref(false)
const error = ref('')
const page = ref(1)
const perPage = ref(10)
const totalPages = ref(0)
const totalStudents = ref(0)
const statusFilter = ref('')
const deletingId = ref(null)

async function fetchStudents() {
  loading.value = true
  error.value = ''
  try {
    const response = await getStudents(page.value, perPage.value, statusFilter.value)
    const data = response.data
    students.value = data.students
    totalPages.value = data.pages
    totalStudents.value = data.total
  } catch (err) {
    error.value = 'Failed to load students. Please try again.'
    students.value = []
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  fetchStudents()
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    fetchStudents()
  }
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value++
    fetchStudents()
  }
}

async function onDelete(student) {
  if (!confirm(`Delete ${student.first_name} ${student.last_name}?`)) return
  deletingId.value = student.id
  try {
    await deleteStudent(student.id)
    await fetchStudents()
  } catch (err) {
    alert('Failed to delete student.')
  } finally {
    deletingId.value = null
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function statusClass(status) {
  return `status-badge status-${status}`
}

// Expose fetchStudents so parent can call it after create/edit
defineExpose({ fetchStudents })

// Initial fetch
fetchStudents()
</script>

<template>
  <div class="student-list">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="filter-group">
        <label for="status-filter">Filter by status:</label>
        <select id="status-filter" v-model="statusFilter" @change="onFilterChange">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="graduated">Graduated</option>
          <option value="dropped">Dropped</option>
        </select>
      </div>
      <div class="total-count" v-if="!loading">
        {{ totalStudents }} student{{ totalStudents !== 1 ? 's' : '' }}
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-message loading">
      <span class="spinner"></span> Loading students...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-message error">
      <p>{{ error }}</p>
      <button @click="fetchStudents" class="btn btn-secondary">Retry</button>
    </div>

    <!-- Empty -->
    <div v-else-if="students.length === 0" class="state-message empty">
      <p>No students found.</p>
    </div>

    <!-- Table -->
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Date of Birth</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id">
            <td>{{ student.first_name }} {{ student.last_name }}</td>
            <td>{{ student.email }}</td>
            <td>{{ formatDate(student.date_of_birth) }}</td>
            <td>
              <span :class="statusClass(student.enrollment_status)">
                {{ student.enrollment_status }}
              </span>
            </td>
            <td class="actions">
              <button @click="emit('edit', student)" class="btn btn-small btn-secondary">
                Edit
              </button>
              <button
                @click="onDelete(student)"
                class="btn btn-small btn-danger"
                :disabled="deletingId === student.id"
              >
                {{ deletingId === student.id ? 'Deleting...' : 'Delete' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button @click="prevPage" :disabled="page <= 1" class="btn btn-secondary">
        ← Previous
      </button>
      <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="page >= totalPages" class="btn btn-secondary">
        Next →
      </button>
    </div>
  </div>
</template>

<style scoped>
.student-list {
  width: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.filter-group select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
}

.total-count {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* States */
.state-message {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-secondary);
}

.state-message.error {
  color: var(--color-danger);
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  text-align: left;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid var(--color-border);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

tbody td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

tbody tr:hover {
  background: var(--color-row-hover);
}

/* Status badges */
.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-graduated {
  background: #dbeafe;
  color: #1e40af;
}

.status-dropped {
  background: #fef3c7;
  color: #92400e;
}

/* Actions */
.actions {
  display: flex;
  gap: 0.5rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
}

.page-info {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
</style>

<script setup>
import { ref, computed } from 'vue'
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

// Compute visible page numbers for numbered pagination
const visiblePages = computed(() => {
  const total = totalPages.value
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const current = page.value
  const pages = []
  pages.push(1)
  if (current > 3) pages.push('...')
  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  if (current < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

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

function goToPage(p) {
  if (p === '...' || p === page.value) return
  page.value = p
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
  if (!confirm(`Are you sure you want to delete ${student.first_name} ${student.last_name}?`)) return
  deletingId.value = student.id
  try {
    await deleteStudent(student.id)
    await fetchStudents()
  } catch (err) {
    alert('Failed to delete student. Please try again.')
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
          <option value="">All Students</option>
          <option value="active">Active</option>
          <option value="graduated">Graduated</option>
          <option value="dropped">Dropped</option>
        </select>
      </div>
      <div class="total-count" v-if="!loading && !error">
        <span class="count-number">{{ totalStudents }}</span>
        student{{ totalStudents !== 1 ? 's' : '' }} found
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="state-card loading-state">
      <div class="spinner-ring"></div>
      <p class="state-title">Loading students...</p>
      <p class="state-subtitle">Fetching data from the server</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="state-card error-state">
      <div class="state-emoji">😕</div>
      <p class="state-title">Failed to load students</p>
      <p class="state-subtitle">Something went wrong while fetching data.</p>
      <button @click="fetchStudents" class="btn btn-primary retry-btn">
        🔄 Retry
      </button>
    </div>

    <!-- Empty state -->
    <div v-else-if="students.length === 0" class="state-card empty-state">
      <div class="state-emoji">📋</div>
      <p class="state-title">No students found</p>
      <p class="state-subtitle" v-if="statusFilter">
        No students with status "{{ statusFilter }}". Try changing the filter.
      </p>
      <p class="state-subtitle" v-else>
        Get started by adding your first student.
      </p>
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
            <th class="th-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in students" :key="student.id" class="student-row">
            <td class="td-name">
              <span class="avatar">{{ student.first_name[0] }}{{ student.last_name[0] }}</span>
              {{ student.first_name }} {{ student.last_name }}
            </td>
            <td class="td-email">{{ student.email }}</td>
            <td>{{ formatDate(student.date_of_birth) }}</td>
            <td>
              <span :class="statusClass(student.enrollment_status)">
                {{ student.enrollment_status }}
              </span>
            </td>
            <td class="td-actions">
              <button @click="emit('edit', student)" class="btn btn-small btn-outline" title="Edit student">
                ✏️ Edit
              </button>
              <button
                @click="onDelete(student)"
                class="btn btn-small btn-danger"
                :disabled="deletingId === student.id"
                title="Delete student"
              >
                {{ deletingId === student.id ? '⏳' : '🗑️' }}
                {{ deletingId === student.id ? 'Deleting...' : 'Delete' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Numbered Pagination -->
    <div v-if="totalPages > 1 && !loading && !error" class="pagination">
      <button
        @click="prevPage"
        :disabled="page <= 1"
        class="btn btn-page btn-nav"
      >
        ← Previous
      </button>

      <div class="page-numbers">
        <button
          v-for="(p, index) in visiblePages"
          :key="index"
          @click="goToPage(p)"
          class="btn btn-page"
          :class="{ 'btn-page-active': p === page, 'btn-page-ellipsis': p === '...' }"
          :disabled="p === '...'"
        >
          {{ p }}
        </button>
      </div>

      <button
        @click="nextPage"
        :disabled="page >= totalPages"
        class="btn btn-page btn-nav"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<style scoped>
.student-list {
  width: 100%;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
  font-weight: 500;
}

.filter-group select {
  padding: 0.45rem 0.85rem;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.total-count {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.count-number {
  font-weight: 700;
  color: var(--color-primary);
}

/* State cards (Loading, Error, Empty) */
.state-card {
  text-align: center;
  padding: 3.5rem 1.5rem;
  border-radius: 12px;
  border: 1.5px dashed var(--color-border);
  background: var(--color-bg);
}

.state-emoji {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.state-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0.5rem 0 0.3rem;
}

.state-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.error-state {
  border-color: #fecaca;
  background: linear-gradient(135deg, #fff5f5, #fff);
}

.error-state .state-title {
  color: #991b1b;
}

.retry-btn {
  margin-top: 1rem;
}

/* Loading spinner */
.spinner-ring {
  display: inline-block;
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--color-border);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  text-align: left;
  padding: 0.85rem 1rem;
  background: var(--color-bg);
  border-bottom: 2px solid var(--color-border);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.th-actions {
  text-align: right;
}

tbody td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
}

tbody tr:last-child td {
  border-bottom: none;
}

.student-row {
  transition: background 0.15s;
}

.student-row:hover {
  background: var(--color-row-hover);
}

/* Avatar */
.td-name {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-weight: 500;
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #818cf8);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  flex-shrink: 0;
}

.td-email {
  color: var(--color-text-secondary);
}

/* Status badges */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: 0.02em;
}

.status-active {
  background: #dcfce7;
  color: #15803d;
}

.status-graduated {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-dropped {
  background: #fef3c7;
  color: #b45309;
}

/* Actions */
.td-actions {
  text-align: right;
}

.td-actions .btn {
  margin-left: 0.4rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  flex-wrap: wrap;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.btn-page {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.25rem;
  height: 2.25rem;
  padding: 0 0.6rem;
  border: 1.5px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-page:hover:not(:disabled):not(.btn-page-active) {
  background: var(--color-bg);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-page-active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
  font-weight: 600;
  cursor: default;
}

.btn-page-ellipsis {
  border: none;
  background: transparent;
  cursor: default;
  min-width: 1.5rem;
  color: var(--color-text-secondary);
}

.btn-nav {
  font-size: 0.825rem;
  padding: 0 0.85rem;
}

@media (max-width: 700px) {
  .td-email {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .btn-nav {
    display: none;
  }
}
</style>

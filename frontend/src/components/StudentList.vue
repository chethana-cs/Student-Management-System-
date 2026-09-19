<script setup>
import { ref, computed } from 'vue'
import { getStudents, deleteStudent } from '@/services/api'
import ConfirmModal from '@/components/ConfirmModal.vue'
import StudentDetailModal from '@/components/StudentDetailModal.vue'

const emit = defineEmits(['edit', 'toast'])

const students = ref([])
const loading = ref(false)
const error = ref('')
const page = ref(1)
const perPage = ref(10)
const totalPages = ref(1)
const totalStudents = ref(0)
const statusFilter = ref('')
const searchQuery = ref('')

// Modal state
const studentToDelete = ref(null)
const deleting = ref(false)
const selectedStudentId = ref(null)
const showDetailModal = ref(false)

// Filter students by search query client-side
const filteredStudents = computed(() => {
  if (!searchQuery.value.trim()) return students.value
  const q = searchQuery.value.toLowerCase().trim()
  return students.value.filter(
    (s) =>
      s.first_name.toLowerCase().includes(q) ||
      s.last_name.toLowerCase().includes(q) ||
      s.email.toLowerCase().includes(q)
  )
})

// Metrics summary calculations
const metrics = computed(() => {
  const active = students.value.filter((s) => s.enrollment_status === 'active').length
  const graduated = students.value.filter((s) => s.enrollment_status === 'graduated').length
  const dropped = students.value.filter((s) => s.enrollment_status === 'dropped').length
  return {
    total: totalStudents.value,
    active,
    graduated,
    dropped,
  }
})

const showingRange = computed(() => {
  if (totalStudents.value === 0) return '0 students'
  const start = (page.value - 1) * perPage.value + 1
  const end = Math.min(page.value * perPage.value, totalStudents.value)
  return `Showing ${start}–${end} of ${totalStudents.value} student${totalStudents.value !== 1 ? 's' : ''}`
})

const visiblePages = computed(() => {
  const total = totalPages.value || 1
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
    totalPages.value = data.pages || 1
    totalStudents.value = data.total || 0
  } catch (err) {
    error.value = 'Failed to load students. Please check your connection and try again.'
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
  if (page.value < (totalPages.value || 1)) {
    page.value++
    fetchStudents()
  }
}

function openViewModal(studentId) {
  selectedStudentId.value = studentId
  showDetailModal.value = true
}

function promptDelete(student) {
  studentToDelete.value = student
}

async function confirmDelete() {
  if (!studentToDelete.value) return
  deleting.value = true
  try {
    await deleteStudent(studentToDelete.value.id)
    emit('toast', { message: `Student ${studentToDelete.value.first_name} deleted.`, type: 'success' })
    studentToDelete.value = null
    await fetchStudents()
  } catch (err) {
    emit('toast', { message: 'Failed to delete student.', type: 'error' })
  } finally {
    deleting.value = false
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + (dateStr.includes('T') ? '' : 'T00:00:00'))
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function statusClass(status) {
  return `status-badge status-${status}`
}

defineExpose({ fetchStudents })

fetchStudents()
</script>

<template>
  <div class="student-list">
    <!-- Compact Metric Summary Bar -->
    <div class="metrics-bar">
      <div class="metric-card">
        <span class="metric-value">{{ metrics.total }}</span>
        <span class="metric-label">Total Students</span>
      </div>
      <div class="metric-card">
        <span class="metric-value text-active">{{ metrics.active }}</span>
        <span class="metric-label">Active</span>
      </div>
      <div class="metric-card">
        <span class="metric-value text-graduated">{{ metrics.graduated }}</span>
        <span class="metric-label">Graduated</span>
      </div>
      <div class="metric-card">
        <span class="metric-value text-dropped">{{ metrics.dropped }}</span>
        <span class="metric-label">Dropped</span>
      </div>
    </div>

    <!-- Toolbar: Search + Filter + Range -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by name or email..."
            class="search-input"
            aria-label="Search students"
          />
        </div>

        <div class="filter-group">
          <label for="status-filter">Status:</label>
          <select id="status-filter" v-model="statusFilter" @change="onFilterChange">
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="graduated">Graduated</option>
            <option value="dropped">Dropped</option>
          </select>
        </div>
      </div>

      <div class="total-count" v-if="!loading && !error">
        {{ showingRange }}
      </div>
    </div>

    <!-- Skeleton Loading State -->
    <div v-if="loading" class="skeleton-wrapper">
      <div v-for="n in 5" :key="n" class="skeleton-row">
        <div class="skeleton-cell sk-avatar"></div>
        <div class="skeleton-cell sk-text sk-wide"></div>
        <div class="skeleton-cell sk-text"></div>
        <div class="skeleton-cell sk-text sk-short"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="state-card error-state">
      <div class="state-emoji">😕</div>
      <p class="state-title">Failed to load students</p>
      <p class="state-subtitle">{{ error }}</p>
      <button @click="fetchStudents" class="btn btn-primary retry-btn">
        🔄 Retry
      </button>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredStudents.length === 0" class="state-card empty-state">
      <div class="state-emoji">📋</div>
      <p class="state-title">No students found</p>
      <p class="state-subtitle" v-if="searchQuery">
        No results matching "{{ searchQuery }}". Try a different search term.
      </p>
      <p class="state-subtitle" v-else-if="statusFilter">
        No students with status "{{ statusFilter }}". Try changing the filter.
      </p>
      <p class="state-subtitle" v-else>
        Get started by adding your first student record.
      </p>
    </div>

    <!-- Table -->
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th class="th-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="student in filteredStudents"
            :key="student.id"
            class="student-row"
            @click="openViewModal(student.id)"
          >
            <td class="td-name">
              <span class="avatar">{{ student.first_name[0] }}{{ student.last_name[0] }}</span>
              {{ student.first_name }} {{ student.last_name }}
            </td>
            <td>
              <span :class="statusClass(student.enrollment_status)">
                {{ student.enrollment_status }}
              </span>
            </td>
            <td class="td-actions" @click.stop>
              <button
                @click="openViewModal(student.id)"
                class="btn btn-small btn-ghost"
                title="View details"
              >
                👁️ View
              </button>
              <button
                @click="emit('edit', student)"
                class="btn btn-small btn-outline"
                title="Edit student"
              >
                ✏️ Edit
              </button>
              <button
                @click="promptDelete(student)"
                class="btn btn-small btn-danger"
                title="Delete student"
              >
                🗑️ Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination Bar -->
    <div v-if="students.length > 0 && !loading && !error" class="pagination-container">
      <div class="pagination-info">
        Page <strong>{{ page }}</strong> of <strong>{{ totalPages || 1 }}</strong>
      </div>
      <div class="pagination-controls">
        <button
          @click="prevPage"
          :disabled="page <= 1"
          class="btn btn-page btn-nav"
          title="Previous page"
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
            :disabled="p === '...' || p === page"
          >
            {{ p }}
          </button>
        </div>

        <button
          @click="nextPage"
          :disabled="page >= totalPages || totalPages <= 1"
          class="btn btn-page btn-nav"
          title="Next page"
        >
          Next →
        </button>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <ConfirmModal
      :show="studentToDelete !== null"
      title="Delete Student Record"
      :message="`Are you sure you want to delete ${studentToDelete?.first_name} ${studentToDelete?.last_name}? This action cannot be undone.`"
      confirmText="Delete Student"
      confirmType="danger"
      :loading="deleting"
      @confirm="confirmDelete"
      @cancel="studentToDelete = null"
    />

    <!-- Student Detail View Modal -->
    <StudentDetailModal
      :show="showDetailModal"
      :studentId="selectedStudentId"
      @close="showDetailModal = false"
      @edit="(s) => emit('edit', s)"
    />
  </div>
</template>

<style scoped>
.student-list {
  width: 100%;
}

/* Metrics Summary Bar */
.metrics-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: var(--color-bg, #f8fafc);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-text, #1e293b);
  line-height: 1.2;
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary, #64748b);
  margin-top: 0.15rem;
}

.text-active { color: #16a34a; }
.text-graduated { color: #2563eb; }
.text-dropped { color: #d97706; }

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.65rem;
  font-size: 0.85rem;
  pointer-events: none;
  opacity: 0.6;
}

.search-input {
  padding: 0.45rem 0.85rem 0.45rem 2.1rem;
  border: 1.5px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #1e293b);
  font-size: 0.85rem;
  width: 220px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.filter-group label {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #64748b);
  font-weight: 500;
}

.filter-group select {
  padding: 0.45rem 0.85rem;
  border: 1.5px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #1e293b);
  font-size: 0.85rem;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-group select:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.total-count {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #64748b);
  font-weight: 500;
}

/* Skeleton Loading */
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.skeleton-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.skeleton-cell {
  background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  height: 1rem;
}

.sk-avatar { width: 2rem; height: 2rem; border-radius: 50%; }
.sk-wide { width: 35%; }
.sk-text { width: 25%; }
.sk-short { width: 15%; }

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* State cards (Error, Empty) */
.state-card {
  text-align: center;
  padding: 3.5rem 1.5rem;
  border-radius: 12px;
  border: 1.5px dashed var(--color-border, #e2e8f0);
  background: var(--color-surface, #ffffff);
}

.state-emoji {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.state-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text, #1e293b);
  margin: 0.5rem 0 0.3rem;
}

.state-subtitle {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

.error-state {
  border-color: #fecaca;
  background: linear-gradient(135deg, #fff5f5, #ffffff);
}

.error-state .state-title { color: #991b1b; }
.retry-btn { margin-top: 1rem; }

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--color-border, #e2e8f0);
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th {
  text-align: left;
  padding: 0.85rem 1rem;
  background: #f8fafc;
  border-bottom: 2px solid var(--color-border, #e2e8f0);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-secondary, #64748b);
  font-weight: 600;
}

.th-actions { text-align: right; }

tbody td {
  padding: 0.8rem 1rem;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
  font-size: 0.9rem;
}

tbody tr:last-child td { border-bottom: none; }

.student-row {
  cursor: pointer;
  transition: background 0.15s;
}

.student-row:hover { background: #f8fafc; }

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
  background: linear-gradient(135deg, #6366f1, #818cf8);
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  flex-shrink: 0;
}

.td-email { color: var(--color-text-secondary, #64748b); }

/* Status badges */
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.7rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-active { background: #dcfce7; color: #15803d; }
.status-graduated { background: #dbeafe; color: #1d4ed8; }
.status-dropped { background: #fef3c7; color: #b45309; }

/* Actions */
.td-actions { text-align: right; }
.td-actions .btn { margin-left: 0.35rem; }

/* Pagination Container */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #e2e8f0);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.pagination-info {
  font-size: 0.85rem;
  color: var(--color-text-secondary, #64748b);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-numbers { display: flex; gap: 0.25rem; }

.btn-page {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.25rem;
  height: 2.25rem;
  padding: 0 0.6rem;
  border: 1.5px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #1e293b);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-page:hover:not(:disabled):not(.btn-page-active) {
  background: #f8fafc;
  border-color: #6366f1;
  color: #6366f1;
}

.btn-page:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-page-active {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
  font-weight: 600;
  cursor: default;
}

.btn-page-ellipsis {
  border: none;
  background: transparent;
  cursor: default;
  min-width: 1.5rem;
  color: var(--color-text-secondary, #64748b);
}

.btn-nav {
  font-size: 0.825rem;
  padding: 0 0.85rem;
}

@media (max-width: 768px) {
  .metrics-bar {
    grid-template-columns: repeat(2, 1fr);
  }
  .search-input {
    width: 100%;
  }
}
</style>

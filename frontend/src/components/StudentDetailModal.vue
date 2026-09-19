<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { getStudent } from '@/services/api'

const props = defineProps({
  studentId: { type: Number, default: null },
  show: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'edit'])

const student = ref(null)
const loading = ref(false)
const error = ref('')

async function fetchDetails(id) {
  if (!id) return
  loading.value = true
  error.value = ''
  try {
    const res = await getStudent(id)
    student.value = res.data
  } catch (err) {
    error.value = 'Failed to load student details.'
    student.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => props.studentId,
  (newId) => {
    if (newId && props.show) {
      fetchDetails(newId)
    }
  },
  { immediate: true }
)

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  const d = new Date(dateStr + (dateStr.includes('T') ? '' : 'T00:00:00'))
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatTimestamp(tsStr) {
  if (!tsStr) return 'N/A'
  const d = new Date(tsStr)
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleKeydown(e) {
  if (e.key === 'Escape' && props.show) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-backdrop" @click.self="emit('close')">
      <div
        class="modal-card"
        role="dialog"
        aria-modal="true"
        aria-label="Student Details"
      >
        <div class="modal-header">
          <h2>Student Details</h2>
          <button @click="emit('close')" class="btn-close" aria-label="Close dialog">
            &times;
          </button>
        </div>

        <div v-if="loading" class="detail-loading">
          <div class="spinner-ring"></div>
          <p>Fetching student details...</p>
        </div>

        <div v-else-if="error" class="detail-error">
          <p>{{ error }}</p>
          <button @click="fetchDetails(studentId)" class="btn btn-ghost btn-small">
            Retry
          </button>
        </div>

        <div v-else-if="student" class="detail-body">
          <div class="profile-card">
            <div class="avatar-large">
              {{ student.first_name[0] }}{{ student.last_name[0] }}
            </div>
            <div class="profile-info">
              <h3>{{ student.first_name }} {{ student.last_name }}</h3>
              <p class="profile-email">{{ student.email }}</p>
              <span class="status-badge" :class="`status-${student.enrollment_status}`">
                {{ student.enrollment_status }}
              </span>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Student ID</span>
              <span class="info-value">#{{ student.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Date of Birth</span>
              <span class="info-value">{{ formatDate(student.date_of_birth) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Record Created</span>
              <span class="info-value">{{ formatTimestamp(student.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Last Updated</span>
              <span class="info-value">{{ formatTimestamp(student.updated_at) }}</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            v-if="student"
            @click="emit('edit', student); emit('close')"
            class="btn btn-primary btn-small"
          >
            Edit Student
          </button>
          <button @click="emit('close')" class="btn btn-ghost btn-small">
            Close
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 41, 59, 0.32);
  backdrop-filter: blur(5px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface, #ffffff);
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  padding: 1.5rem;
  box-shadow: 0 24px 60px -28px rgba(15, 23, 42, 0.45);
  border: 1px solid var(--color-border, #e2e8f0);
  animation: modalPop 0.2s ease-out;
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
}

.modal-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-text, #1e293b);
}

.btn-close {
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
}

.btn-close:hover {
  color: #475569;
}

.detail-loading,
.detail-error {
  padding: 2.5rem;
  text-align: center;
}

.detail-body {
  padding: 1.25rem 0 0.5rem;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  background: linear-gradient(135deg, #e9f7f3, #f8fcf9);
  border-radius: 12px;
  border: 1px solid #cde9df;
}

.avatar-large {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #0f766e, #5db8a8);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  text-transform: uppercase;
}

.profile-info h3 {
  margin: 0 0 0.2rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
}

.profile-email {
  margin: 0 0 0.4rem;
  font-size: 0.85rem;
  color: #64748b;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-active { background: #dcfce7; color: #15803d; }
.status-graduated { background: #dff4ef; color: #0f766e; }
.status-dropped { background: #fef3c7; color: #b45309; }

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.85rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  background: #ffffff;
  padding: 0.65rem 0.85rem;
  border-radius: 10px;
  border: 1px solid var(--color-border, #e2e8f0);
}

.info-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.info-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin-top: 0.15rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border, #e2e8f0);
  margin-top: 1rem;
}

.spinner-ring {
  display: inline-block;
  width: 1.75rem;
  height: 1.75rem;
  border: 2px solid #e2e8f0;
  border-top-color: #0f766e;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

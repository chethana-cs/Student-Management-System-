<script setup>
import { ref, computed, watch } from 'vue'
import { createStudent, updateStudent } from '@/services/api'

const props = defineProps({
  student: { type: Object, default: null },
})

const emit = defineEmits(['saved', 'cancel'])

const isEdit = computed(() => props.student !== null)

const form = ref(getEmptyForm())
const fieldErrors = ref({})
const apiError = ref('')
const submitting = ref(false)
const touched = ref({})

function getEmptyForm() {
  return {
    first_name: '',
    last_name: '',
    email: '',
    date_of_birth: '',
    enrollment_status: 'active',
  }
}

watch(
  () => props.student,
  (s) => {
    if (s) {
      form.value = {
        first_name: s.first_name,
        last_name: s.last_name,
        email: s.email,
        date_of_birth: s.date_of_birth,
        enrollment_status: s.enrollment_status,
      }
    } else {
      form.value = getEmptyForm()
    }
    fieldErrors.value = {}
    apiError.value = ''
    touched.value = {}
  },
  { immediate: true }
)

function markTouched(field) {
  touched.value[field] = true
  validateField(field)
}

function validateField(field) {
  const errs = { ...fieldErrors.value }
  delete errs[field]

  const val = form.value[field]

  if (field === 'first_name') {
    if (!val || !val.trim()) errs.first_name = 'First name is required.'
  }
  if (field === 'last_name') {
    if (!val || !val.trim()) errs.last_name = 'Last name is required.'
  }
  if (field === 'email') {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!val || !val.trim()) {
      errs.email = 'Email is required.'
    } else if (!emailPattern.test(val.trim())) {
      errs.email = 'Please enter a valid email address.'
    }
  }
  if (field === 'date_of_birth') {
    if (!val) {
      errs.date_of_birth = 'Date of birth is required.'
    } else {
      const dob = new Date(val + 'T00:00:00')
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      if (isNaN(dob.getTime())) {
        errs.date_of_birth = 'Please enter a valid date.'
      } else if (dob > today) {
        errs.date_of_birth = 'Date of birth cannot be in the future.'
      }
    }
  }
  if (field === 'enrollment_status') {
    if (!val) errs.enrollment_status = 'Enrollment status is required.'
  }

  fieldErrors.value = errs
}

function validateAll() {
  const fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'enrollment_status']
  fields.forEach((f) => {
    touched.value[f] = true
    validateField(f)
  })
  return Object.keys(fieldErrors.value).length === 0
}

async function onSubmit() {
  if (!validateAll()) return

  apiError.value = ''
  submitting.value = true

  const payload = {
    first_name: form.value.first_name.trim(),
    last_name: form.value.last_name.trim(),
    email: form.value.email.trim(),
    date_of_birth: form.value.date_of_birth,
    enrollment_status: form.value.enrollment_status,
  }

  try {
    if (isEdit.value) {
      await updateStudent(props.student.id, payload)
      emit('saved', 'update')
    } else {
      await createStudent(payload)
      emit('saved', 'create')
    }
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data
      if (data.details) {
        apiError.value = Array.isArray(data.details) ? data.details.join(' ') : data.details
      } else if (data.error) {
        apiError.value = data.error
      } else {
        apiError.value = 'An unexpected error occurred.'
      }
    } else {
      apiError.value = 'Network error. Please check your backend connection.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="student-form" role="region" aria-label="Student Form">
    <div class="form-header">
      <div class="form-icon">{{ isEdit ? '✏️' : '➕' }}</div>
      <h2>{{ isEdit ? 'Edit Student Record' : 'Add New Student' }}</h2>
    </div>

    <!-- API error banner -->
    <div v-if="apiError" class="error-banner" role="alert">
      <span class="error-icon">⚠️</span>
      <span>{{ apiError }}</span>
    </div>

    <form @submit.prevent="onSubmit" novalidate>
      <div class="form-row">
        <div class="form-group" :class="{ 'has-error': touched.first_name && fieldErrors.first_name }">
          <label for="first_name">First Name <span class="required">*</span></label>
          <input
            id="first_name"
            v-model="form.first_name"
            type="text"
            placeholder="e.g. Jane"
            :disabled="submitting"
            @blur="markTouched('first_name')"
            @input="validateField('first_name')"
          />
          <p v-if="touched.first_name && fieldErrors.first_name" class="field-error">
            {{ fieldErrors.first_name }}
          </p>
        </div>
        <div class="form-group" :class="{ 'has-error': touched.last_name && fieldErrors.last_name }">
          <label for="last_name">Last Name <span class="required">*</span></label>
          <input
            id="last_name"
            v-model="form.last_name"
            type="text"
            placeholder="e.g. Doe"
            :disabled="submitting"
            @blur="markTouched('last_name')"
            @input="validateField('last_name')"
          />
          <p v-if="touched.last_name && fieldErrors.last_name" class="field-error">
            {{ fieldErrors.last_name }}
          </p>
        </div>
      </div>

      <div class="form-group" :class="{ 'has-error': touched.email && fieldErrors.email }">
        <label for="email">Email Address <span class="required">*</span></label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="e.g. jane.doe@example.com"
          :disabled="submitting"
          @blur="markTouched('email')"
          @input="validateField('email')"
        />
        <p v-if="touched.email && fieldErrors.email" class="field-error">
          {{ fieldErrors.email }}
        </p>
      </div>

      <div class="form-row">
        <div class="form-group" :class="{ 'has-error': touched.date_of_birth && fieldErrors.date_of_birth }">
          <label for="date_of_birth">Date of Birth <span class="required">*</span></label>
          <input
            id="date_of_birth"
            v-model="form.date_of_birth"
            type="date"
            :disabled="submitting"
            @blur="markTouched('date_of_birth')"
            @change="validateField('date_of_birth')"
          />
          <p v-if="touched.date_of_birth && fieldErrors.date_of_birth" class="field-error">
            {{ fieldErrors.date_of_birth }}
          </p>
        </div>
        <div class="form-group">
          <label for="enrollment_status">Enrollment Status <span class="required">*</span></label>
          <select
            id="enrollment_status"
            v-model="form.enrollment_status"
            :disabled="submitting"
          >
            <option value="active">Active</option>
            <option value="graduated">Graduated</option>
            <option value="dropped">Dropped</option>
          </select>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="btn-spinner"></span>
          {{ submitting ? 'Saving...' : (isEdit ? 'Update Student' : 'Add Student') }}
        </button>
        <button type="button" @click="emit('cancel')" class="btn btn-ghost" :disabled="submitting">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.student-form {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
}

.form-icon {
  font-size: 1.2rem;
}

h2 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-icon {
  flex-shrink: 0;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 0.35rem;
}

.required {
  color: var(--color-danger, #ef4444);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.55rem 0.85rem;
  border: 1.5px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  font-size: 0.875rem;
  background: #ffffff;
  color: var(--color-text, #0f172a);
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary, #6366f1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.form-group.has-error input,
.form-group.has-error select {
  border-color: var(--color-danger, #ef4444);
}

.form-group.has-error input:focus,
.form-group.has-error select:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.12);
}

.field-error {
  margin: 0.3rem 0 0;
  font-size: 0.8rem;
  color: var(--color-danger, #ef4444);
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
}

.btn-spinner {
  display: inline-block;
  width: 0.85rem;
  height: 0.85rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.4rem;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>

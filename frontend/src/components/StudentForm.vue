<script setup>
import { ref, computed, watch } from 'vue'
import { createStudent, updateStudent } from '@/services/api'

const props = defineProps({
  student: { type: Object, default: null },
})

const emit = defineEmits(['saved', 'cancel'])

const isEdit = computed(() => props.student !== null)

const form = ref(getEmptyForm())
const errors = ref([])
const apiError = ref('')
const submitting = ref(false)

function getEmptyForm() {
  return {
    first_name: '',
    last_name: '',
    email: '',
    date_of_birth: '',
    enrollment_status: 'active',
  }
}

// When student prop changes (edit mode), populate the form
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
    errors.value = []
    apiError.value = ''
  },
  { immediate: true }
)

function validate() {
  const errs = []

  if (!form.value.first_name.trim()) {
    errs.push('First name is required.')
  }
  if (!form.value.last_name.trim()) {
    errs.push('Last name is required.')
  }

  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!form.value.email.trim()) {
    errs.push('Email is required.')
  } else if (!emailPattern.test(form.value.email.trim())) {
    errs.push('Please enter a valid email address.')
  }

  if (!form.value.date_of_birth) {
    errs.push('Date of birth is required.')
  } else {
    const dob = new Date(form.value.date_of_birth + 'T00:00:00')
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    if (isNaN(dob.getTime())) {
      errs.push('Date of birth must be a valid date.')
    } else if (dob > today) {
      errs.push('Date of birth cannot be in the future.')
    }
  }

  if (!form.value.enrollment_status) {
    errs.push('Enrollment status is required.')
  }

  return errs
}

async function onSubmit() {
  errors.value = validate()
  if (errors.value.length > 0) return

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
    } else {
      await createStudent(payload)
    }
    emit('saved')
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data
      if (data.details) {
        apiError.value = data.details.join(' ')
      } else if (data.error) {
        apiError.value = data.error
      } else {
        apiError.value = 'An unexpected error occurred.'
      }
    } else {
      apiError.value = 'Network error. Please check your connection.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="student-form">
    <h2>{{ isEdit ? 'Edit Student' : 'Add New Student' }}</h2>

    <!-- Client-side validation errors -->
    <div v-if="errors.length > 0" class="error-box">
      <p v-for="(err, i) in errors" :key="i">{{ err }}</p>
    </div>

    <!-- API errors -->
    <div v-if="apiError" class="error-box api-error">
      <p>{{ apiError }}</p>
    </div>

    <form @submit.prevent="onSubmit">
      <div class="form-row">
        <div class="form-group">
          <label for="first_name">First Name</label>
          <input
            id="first_name"
            v-model="form.first_name"
            type="text"
            placeholder="e.g. Jane"
            :disabled="submitting"
          />
        </div>
        <div class="form-group">
          <label for="last_name">Last Name</label>
          <input
            id="last_name"
            v-model="form.last_name"
            type="text"
            placeholder="e.g. Doe"
            :disabled="submitting"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="e.g. jane@example.com"
          :disabled="submitting"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="date_of_birth">Date of Birth</label>
          <input
            id="date_of_birth"
            v-model="form.date_of_birth"
            type="date"
            :disabled="submitting"
          />
        </div>
        <div class="form-group">
          <label for="enrollment_status">Status</label>
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
          {{ submitting ? 'Saving...' : (isEdit ? 'Update Student' : 'Add Student') }}
        </button>
        <button type="button" @click="emit('cancel')" class="btn btn-secondary" :disabled="submitting">
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.student-form {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

h2 {
  margin: 0 0 1rem;
  font-size: 1.15rem;
  color: var(--color-text);
}

.error-box {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
}

.error-box p {
  margin: 0.15rem 0;
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
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.3rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
</style>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure you want to proceed?' },
  confirmText: { type: String, default: 'Delete' },
  confirmType: { type: String, default: 'danger' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])

function handleKeydown(e) {
  if (e.key === 'Escape' && props.show && !props.loading) {
    emit('cancel')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-backdrop" @click.self="!loading && emit('cancel')">
      <div
        class="modal-card"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
      >
        <div class="modal-icon" :class="`icon-${confirmType}`">
          ⚠️
        </div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-message">{{ message }}</p>

        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-ghost"
            :disabled="loading"
            @click="emit('cancel')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn"
            :class="confirmType === 'danger' ? 'btn-danger-solid' : 'btn-primary'"
            :disabled="loading"
            @click="emit('confirm')"
          >
            <span v-if="loading" class="btn-spinner"></span>
            {{ loading ? 'Processing...' : confirmText }}
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
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  background: var(--color-surface, #ffffff);
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--color-border, #e2e8f0);
  animation: modalPop 0.2s ease-out;
}

@keyframes modalPop {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.75rem;
  font-size: 1.25rem;
}

.icon-danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text, #1e293b);
  margin-bottom: 0.4rem;
}

.modal-message {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.modal-actions .btn {
  flex: 1;
}

.btn-danger-solid {
  background: #ef4444;
  color: #ffffff;
  border: none;
}

.btn-danger-solid:hover:not(:disabled) {
  background: #dc2626;
}
</style>

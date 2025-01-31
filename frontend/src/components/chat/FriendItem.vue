<template>
  <div class="friend-item">
    <div class="friend-item__info">
      <div
        class="friend-item__status-indicator"
        :class="{ online: isOnline }"
      ></div>
      <span class="friend-item__name">{{ friend.username }}</span>
    </div>
    <div class="friend-item__actions">
      <button
        @click="$emit('chat', friend)"
        class="friend-item__action-btn"
        :title="$t('friendList.chat')"
      >
        <span class="material-icons">{{ $t('friendList.icons.chat') }}</span>
      </button>
      <button
        @click="goToProfile(friend)"
        class="friend-item__action-btn"
        :title="$t('friendList.profile')"
      >
        <span class="material-icons">{{ $t('friendList.icons.profile') }}</span>
      </button>
      <button
        @click="$emit('block', friend)"
        class="friend-item__action-btn"
        :title="$t('friendList.block')"
      >
        <span class="material-icons">{{ $t('friendList.icons.block') }}</span>
      </button>
      <button
        @click="$emit('delete', friend)"
        class="friend-item__action-btn"
        :title="$t('friendList.delete')"
      >
        <span class="material-icons">{{ $t('friendList.icons.delete') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useUserStatus } from '@/composables/useUserStatus'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  friend: {
    type: Object,
    required: true,
  },
})

const { onlineUsers } = useUserStatus()

const isOnline = computed(() => {
  return onlineUsers.value.has(props.friend.id)
})

const goToProfile = async (friend) => {
  // Si on est déjà sur un profil, on force le rechargement
  if (router.currentRoute.value.name === 'profil') {
    await router.push('/') // On redirige d'abord vers la home
  }
  router.push(`/${friend.id}/profil`)
}

defineEmits(['chat', 'block', 'delete'])
</script>

<style scoped>
.friend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid var(--secondary-color);
}

.friend-item__info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.friend-item__status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--error-color);
}

.friend-item__status-indicator.online {
  background-color: var(--success-color);
}

.friend-item__actions {
  display: flex;
  gap: 5px;
}

.friend-item__action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color);
  padding: 4px;
}

.friend-item__action-btn:hover {
  color: var(--primary-color);
}

.friend-item__name {
  color: var(--text-color);
}
</style>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../../stores/authStore'
import axios from 'axios'

const emit = defineEmits(['showNotification'])
const authStore = useAuthStore()

// Référence vers l'input file caché
const fileInput = ref(null)
const selectedFile = ref(null)

const profilePhotoUrl = computed(() => {
  if (selectedFile.value) {
    return URL.createObjectURL(selectedFile.value)
  }
  return authStore.user?.profile_picture
    ? `http://localhost:8000${authStore.user.profile_picture}`
    : null
})

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const saveProfilePhoto = async () => {
  if (!selectedFile.value) return

  // Vérifier la taille du fichier (2Mo max)
  if (selectedFile.value.size > 2 * 1024 * 1024) {
    emit('showNotification', {
      message: "La taille de l'image ne doit pas dépasser 2 Mo",
      type: 'error',
    })
    return
  }

  const formData = new FormData()
  formData.append('profile_picture', selectedFile.value)

  try {
    const response = await axios.put(
      `/users/update_profile_picture/${authStore.user.id}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      }
    )

    if (response.data.message === 'Profile picture updated successfully') {
      emit('showNotification', {
        message: 'Photo de profil mise à jour avec succès',
        type: 'success',
      })

      const userResponse = await axios.get(
        `/users/read/${authStore.user.id}`,
        { withCredentials: true }
      )
      if (userResponse.data) {
        authStore.updateUser(userResponse.data)
      }
      selectedFile.value = null
    }
  } catch (error) {
    emit('showNotification', {
      message:
        error.response?.data?.error ||
        'Erreur lors de la mise à jour de la photo de profil',
      type: 'error',
    })
  }
}
</script>

<template>
  <div class="profile-section">
    <h3>{{ $t('settings.profilePhoto') }}</h3>
    <div class="profile-photo-container">
      <img
        :src="profilePhotoUrl"
        :alt="$t('settings.profilePhoto')"
        class="profile-photo"
      />
      <div class="photo-overlay" @click="triggerFileInput">
        <span>{{ $t('settings.clickToChange') }}</span>
      </div>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileSelect"
      style="display: none"
    />
    <button
      class="save-button"
      @click="saveProfilePhoto"
      :disabled="!selectedFile"
    >
      <i class="icon-save"></i> {{ $t('settings.save') }}
    </button>
  </div>
</template>

<style scoped>
.profile-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  border: 1px solid var(--secondary-color);
  text-align: center;
}

.profile-photo-container {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto;
  cursor: pointer;
}

.profile-photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  transition: filter 0.3s ease;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.photo-overlay span {
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 14px;
}

.profile-photo-container:hover .photo-overlay {
  opacity: 1;
}

.profile-photo-container:hover .profile-photo {
  filter: brightness(0.8);
}

.save-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
}

.save-button:hover {
  background: var(--primary-hover-color);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

h3 {
  color: var(--text-color);
  margin: 0;
}
</style>

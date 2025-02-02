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
    ? `https://c2r2p6:8443${authStore.user.profile_picture}`
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
  gap: 2rem;
  padding: 2rem;
  background: var(--background-secondary-color);
  border-radius: 15px;
  border: 2px solid var(--primary-color);
  text-align: center;
  box-shadow: 0 8px 25px var(--primary-shadow-color);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: fadeIn 0.6s ease;
}

.profile-section:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px var(--primary-shadow-color);
}

.profile-photo-container {
  position: relative;
  width: 180px;
  height: 180px;
  margin: 0 auto;
  cursor: pointer;
  border-radius: 50%;
  box-shadow: 0 5px 15px var(--primary-shadow-color);
  transition: all 0.3s ease;
}

.profile-photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--primary-color);
  transition: all 0.3s ease;
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(52, 152, 219, 0.9),
    rgba(41, 128, 185, 0.9)
  );
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: all 0.3s ease;
  transform: scale(0.9);
}

.photo-overlay span {
  color: white;
  text-align: center;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 600;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.profile-photo-container:hover {
  transform: scale(1.05);
}

.profile-photo-container:hover .photo-overlay {
  opacity: 1;
  transform: scale(1);
}

.profile-photo-container:hover .photo-overlay span {
  opacity: 1;
  transform: translateY(0);
}

.profile-photo-container:hover .profile-photo {
  filter: brightness(0.8);
  transform: scale(0.95);
}

.save-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover-color));
  color: var(--text-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  font-weight: 600;
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

.save-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.save-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px var(--primary-shadow-color);
}

.save-button:hover::before {
  opacity: 1;
}

.save-button:active {
  transform: translateY(-1px);
}

.save-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--text-secondary-color);
}

h3 {
  color: var(--primary-color);
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 0 0 10px var(--primary-shadow-color);
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Media Queries */
@media (max-width: 768px) {
  .profile-section {
    padding: 1.5rem;
    gap: 1.5rem;
  }

  .profile-photo-container {
    width: 150px;
    height: 150px;
  }

  h3 {
    font-size: 1.5rem;
  }

  .save-button {
    padding: 0.8rem 1.5rem;
    font-size: 0.9rem;
  }
}
</style>
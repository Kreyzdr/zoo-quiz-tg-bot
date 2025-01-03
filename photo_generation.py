"""ИИ которая создаёт фото"""

import os
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array
import tensorflow as tf
from tensorflow.keras import layers

# Путь к вашему набору данных
data_directory = 'animals_dataset'

# Загрузка и изменение размера изображений
images = []
for filename in os.listdir(data_directory):
    img_path = os.path.join(data_directory, filename)
    img = Image.open(img_path).resize((64, 64))  # Изменение размера до 64x64 пикселей
    img_array = img_to_array(img) / 255.0  # Нормализация
    images.append(img_array)

# Преобразование в массив NumPy
images_array = np.array(images)

print("Количество загруженных изображений:", len(images_array))



def build_generator():
    model = tf.keras.Sequential()

    model.add(layers.Dense(8 * 8 * 128, input_dim=100))  # Входной слой
    model.add(layers.Reshape((8, 8, 128)))  # Преобразование в 3D
    model.add(layers.Conv2DTranspose(128, (4, 4), strides=(2, 2), padding='same'))
    model.add(layers.Activation('relu'))
    model.add(layers.Conv2DTranspose(64, (4, 4), strides=(2, 2), padding='same'))
    model.add(layers.Activation('relu'))
    model.add(layers.Conv2DTranspose(3, (7, 7), padding='same'))
    model.add(layers.Activation('tanh'))

    return model


generator = build_generator()
generator.summary()


def build_discriminator():
    model = tf.keras.Sequential()

    model.add(layers.Conv2D(64, (3, 3), strides=(2, 2), input_shape=(64, 64, 3)))
    model.add(layers.LeakyReLU(alpha=0.2))
    model.add(layers.Dropout(0.3))
    model.add(layers.Conv2D(128, (3, 3), strides=(2, 2)))
    model.add(layers.LeakyReLU(alpha=0.2))
    model.add(layers.Dropout(0.3))
    model.add(layers.Flatten())
    model.add(layers.Dense(1, activation='sigmoid'))

    return model


discriminator = build_discriminator()
discriminator.summary()

# Компилируем дискриминатор
discriminator.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Создаем GAN
discriminator.trainable = False
gan_input = layers.Input(shape=(100,))
generated_image = generator(gan_input)
gan_output = discriminator(generated_image)
gan = tf.keras.Model(gan_input, gan_output)

# Компилируем GAN
gan.compile(loss='binary_crossentropy', optimizer='adam')


# Функция обучения
def train_gan(epochs, batch_size):
    for epoch in range(epochs):
        # Обучение дискриминатора
        idx = np.random.randint(0, images.shape[0], batch_size)
        real_images = images[idx]

        noise = np.random.normal(0, 1, (batch_size, 100))
        fake_images = generator.predict(noise)

        d_loss_real = discriminator.train_on_batch(real_images, np.ones((batch_size, 1)))
        d_loss_fake = discriminator.train_on_batch(fake_images, np.zeros((batch_size, 1)))

        # Обучение генератора
        noise = np.random.normal(0, 1, (batch_size, 100))
        g_loss = gan.train_on_batch(noise, np.ones((batch_size, 1)))

        if epoch % 100 == 0:
            print(f"Epoch {epoch} | D Loss: {0.5 * (d_loss_real[0] + d_loss_fake[0])} | G Loss: {g_loss}")


# Запуск обучения
train_gan(epochs=5000, batch_size=1270)

import matplotlib.pyplot as plt

def generate_images(num_images):
    noise = np.random.normal(0, 1, (num_images, 100))
    generated_images = generator.predict(noise)

    plt.figure(figsize=(10, 10))
    for i in range(num_images):
        plt.subplot(4, 4, i + 1)
        plt.imshow(generated_images[i])
        plt.axis('off')
    plt.show()

print(generate_images(16) ) # Генерация 16 изображений
import { Container, Main } from '../../components';
import { Helmet } from 'react-helmet';
import styles from './styles.module.css';

const About = () => {
    return (
        <Main>
            <Helmet>
                <title>О проекте — Foodgram</title>
                <meta
                    name="description"
                    content="Foodgram — платформа для публикации и поиска кулинарных рецептов."
                />
                <meta property="og:title" content="О проекте — Foodgram" />
                <meta
                    property="og:description"
                    content="Узнайте, как работает платформа для рецептов Foodgram."
                />
            </Helmet>

            <Container>
                <h1 className={styles.title}>О проекте</h1>
                <div className={styles.content}>
                    <div className={styles.mainText}>
                        <h2 className={styles.subtitle}>
                            Что такое Foodgram?
                        </h2>
                        <p className={styles.textItem}>
                            Foodgram — это онлайн-платформа, где пользователи
                            могут
                            <strong>
                                {' '}
                                публиковать, просматривать и сохранять
                            </strong>
                            кулинарные рецепты. Здесь легко найти вдохновение
                            для ужина, составить список покупок и поделиться
                            своими кулинарными находками с другими.
                        </p>
                        <p className={styles.textItem}>
                            Этот проект был разработан в рамках учебного курса
                            <a
                                href="https://practicum.yandex.ru"
                                className={styles.textLink}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                Яндекс Практикум
                            </a>{' '}
                            как часть финального задания. Всё, от дизайна до
                            бэкенда и фронтенда — сделано с нуля.
                        </p>
                        <p className={styles.textItem}>
                            <strong>Возможности сайта:</strong>
                            <ul className={styles.list}>
                                <li>
                                    Публикация своих рецептов с фото и
                                    пошаговыми инструкциями
                                </li>
                                <li>
                                    Поиск рецептов по тегам (завтрак, обед,
                                    ужин, десерт)
                                </li>
                                <li>Добавление рецептов в «Избранное»</li>
                                <li>Подписка на любимых авторов</li>
                                <li>
                                    Автоматическая генерация списка покупок
                                </li>
                            </ul>
                        </p>
                        <p className={styles.textItem}>
                            Для доступа ко всем функциям необходима{' '}
                            <strong>регистрация</strong>. Подтверждение email
                            не требуется — вы можете использовать любой адрес.
                        </p>
                    </div>

                    <aside className={styles.sidebar}>
                        <h2 className={styles.additionalTitle}>
                            Полезные ссылки
                        </h2>
                        <div className={styles.links}>
                            <p className={styles.textItem}>
                                📁 Исходный код проекта:
                                <a
                                    href="https://github.com/VladislavAndrievskis/foodgram"
                                    className={styles.textLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    GitHub
                                </a>
                            </p>
                            <p className={styles.textItem}>
                                👨‍💻 Автор:
                                <a
                                    href="https://github.com/VladislavAndrievskis"
                                    className={styles.textLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Vladislav Andrievskis
                                </a>
                            </p>
                            <p className={styles.textItem}>
                                🎓 Курс:
                                <a
                                    href="https://practicum.yandex.ru"
                                    className={styles.textLink}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    Яндекс Практикум — Веб-разработка
                                </a>
                            </p>
                        </div>
                    </aside>
                </div>
            </Container>
        </Main>
    );
};

export default About;
























import { Container, Main } from '../../components';
import { Helmet } from 'react-helmet';
import styles from './styles.module.css';

const Technologies = () => {
    return (
        <Main>
            <Helmet>
                <title>Технологии — Foodgram</title>
                <meta
                    name="description"
                    content="Технологический стек проекта Foodgram: Python, Django, React, Docker и другие."
                />
                <meta property="og:title" content="Технологии — Foodgram" />
                <meta
                    property="og:description"
                    content="Какие технологии использовались при разработке платформы для рецептов Foodgram."
                />
            </Helmet>

            <Container>
                <h1 className={styles.title}>Технологии</h1>
                <div className={styles.content}>
                    <div className={styles.mainText}>
                        <h2 className={styles.subtitle}>
                            На чём построен Foodgram
                        </h2>
                        <p className={styles.textItem}>
                            Этот проект реализован с использованием современных
                            технологий на бэкенде и фронтенде. Ниже — основной
                            стек, который был применён при разработке.
                        </p>

                        <h3 className={styles.subsubtitle}>Бэкенд</h3>
                        <ul className={styles.list}>
                            <li>
                                <strong>Python 3</strong> — основной язык
                                программирования
                            </li>
                            <li>
                                <strong>Django</strong> — фреймворк для
                                создания веб-приложений
                            </li>
                            <li>
                                <strong>Django REST Framework (DRF)</strong> —
                                для построения RESTful API
                            </li>
                            <li>
                                <strong>Djoser</strong> — библиотека для
                                аутентификации по токенам
                            </li>
                            <li>
                                <strong>PostgreSQL</strong> — основная база
                                данных в продакшене
                            </li>
                            <li>
                                <strong>Simple JWT</strong> — для генерации и
                                управления JWT-токенами
                            </li>
                        </ul>

                        <h3 className={styles.subsubtitle}>Фронтенд</h3>
                        <ul className={styles.list}>
                            <li>
                                <strong>React</strong> — библиотека для
                                создания пользовательского интерфейса
                            </li>
                            <li>
                                <strong>React Router</strong> — навигация между
                                страницами
                            </li>
                            <li>
                                <strong>react-helmet</strong> — управление
                                мета-тегами
                            </li>
                            <li>
                                <strong>CSS Modules</strong> — локальные стили
                                для компонентов
                            </li>
                        </ul>

                        <h3 className={styles.subsubtitle}>Инфраструктура</h3>
                        <ul className={styles.list}>
                            <li>
                                <strong>Docker</strong> — контейнеризация
                                приложения
                            </li>
                            <li>
                                <strong>Docker Compose</strong> — оркестрация
                                сервисов (бэкенд, база, Nginx)
                            </li>
                            <li>
                                <strong>Nginx</strong> — веб-сервер для раздачи
                                статики и проксирования
                            </li>
                            <li>
                                <strong>Gunicorn</strong> — WSGI-сервер для
                                запуска Django
                            </li>
                            <li>
                                <strong>GitHub Actions</strong> — CI/CD и
                                автоматизация тестов
                            </li>
                            <li>
                                <strong>
                                    Yandex Cloud / AWS / другой хостинг
                                </strong>{' '}
                                — развертывание проекта
                            </li>
                        </ul>

                        <p className={styles.textItem}>
                            Все технологии выбраны с учётом масштабируемости,
                            безопасности и удобства поддержки. Архитектура
                            позволяет легко добавлять новые функции и
                            интеграции.
                        </p>
                    </div>
                </div>
            </Container>
        </Main>
    );
};

export default Technologies;

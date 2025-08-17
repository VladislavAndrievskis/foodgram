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

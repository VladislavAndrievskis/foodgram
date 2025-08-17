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
                                    Ваше Имя
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

import React, { useContext } from 'react';
import styles from './style.module.css';

import { AuthContext } from '../../context/authContext';
import Account from '../account';
import { LinkComponent } from '../index.js';

// Меню для незалогиненных
const NotLoggedInMenu = [
    { title: 'Войти', href: '/signin' },
    { title: 'Регистрация', href: '/signup' },
];

const AccountMenu = ({ onSignOut, orders }) => {
    const authContext = useContext(AuthContext);
    const location = window.location; // useLocation не доступен здесь

    if (!authContext) {
        return (
            <div className={styles.menu}>
                {NotLoggedInMenu.map(item => {
                    return location.pathname === item.href ? (
                        <button
                            key={item.href}
                            type="button"
                            className={`${styles.menuButton} ${styles.menuButton_dark}`}
                        >
                            {item.title}
                        </button>
                    ) : (
                        <LinkComponent
                            key={item.href}
                            title={item.title}
                            href={item.href}
                            exact
                            className={styles.menuLink}
                        />
                    );
                })}
            </div>
        );
    }

    return (
        <div className={styles.menu}>
            <Account onSignOut={onSignOut} orders={orders} />
        </div>
    );
};

export default AccountMenu;

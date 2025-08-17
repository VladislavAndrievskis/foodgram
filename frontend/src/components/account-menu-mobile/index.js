// src/components/account-menu-mobile/AccountMenuMobile.js
import React, { useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { Button, LinkComponent } from '../index.js';
import AuthContext from '../../contexts/auth-context'; // ⚠️ проверь путь
import AccountMobile from '../account-mobile';
import cn from 'classnames';
import styles from './styles.module.css'; // ⚠️ убедись, что имя файла: style.module.css

// Меню для неавторизованного пользователя
const NotLoggedInMenu = [
 { title: 'Войти', href: '/signin' },
 { title: 'Создать аккаунт', href: '/signup' },
];

const AccountMenuMobile = ({ onSignOut, orders }) => {
 const authContext = useContext(AuthContext);
 const location = useLocation();

 if (!authContext) {
 return (
 <div className={styles.menu}>
 {NotLoggedInMenu.map(item => (
 location.pathname === item.href ? (
 <Button
 key={item.href}
 href={item.href}
 modifier="style_dark"
 className={cn(styles.menuButton, styles.menuButton_mobile)}
 >
 {item.title}
 </Button>
 ) : (
 <LinkComponent
 key={item.href}
 title={item.title}
 href={item.href}
 exact
 className={cn(styles.menuLink, styles.menuLink_mobile)}
 />
 )
 ))}
 </div>
 );
 }

 return (
 <div className={styles.menu}>
 <AccountMobile onSignOut={onSignOut} orders={orders} />
 </div>
 );
};

export default AccountMenuMobile; // ✅ Экспорт добавлен

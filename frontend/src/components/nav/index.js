import styles from './style.module.css';

import { useEffect, useState } from 'react';

// Прямые импорты — надёжнее и понятнее
import AccountMenu from '../account-menu';
import AccountMenuMobile from '../account-menu-mobile';
import NavMenu from '../nav-menu';
import Orders from '../orders';
import LinkComponent from '../link-component';

import cn from 'classnames';
import { useLocation } from 'react-router-dom';

import hamburgerImg from '../../images/hamburger-menu.png';
import hamburgerImgClose from '../../images/hamburger-menu-close.png';

const Nav = ({ loggedIn, onSignOut, orders }) => {
    const [menuToggled, setMenuToggled] = useState(false);
    const location = useLocation();

    useEffect(() => {
        const handleResize = () => setMenuToggled(false);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        setMenuToggled(false);
    }, [location.pathname]);

    return (
        <div className={styles.nav}>
            {/* Кнопка заказов */}
            <LinkComponent
                href="/cart"
                className={styles.nav__orders}
                title={<Orders orders={orders} />}
            />

            {/* Кнопка бургер-меню */}
            <div
                className={styles.menuButton}
                onClick={() => setMenuToggled(!menuToggled)}
            >
                <img
                    src={menuToggled ? hamburgerImgClose : hamburgerImg}
                    alt="Меню"
                />
            </div>

            {/* Десктопное меню */}
            <div className={styles.nav__container}>
                <NavMenu loggedIn={loggedIn} />
                <AccountMenu onSignOut={onSignOut} orders={orders} />
            </div>

            {/* Мобильное меню */}
            <div
                className={cn(styles['nav__container-mobile'], {
                    [styles['nav__container-mobile_visible']]: menuToggled,
                })}
            >
                <NavMenu loggedIn={loggedIn} />
                <AccountMenuMobile onSignOut={onSignOut} orders={orders} />
            </div>
        </div>
    );
};

export default Nav;

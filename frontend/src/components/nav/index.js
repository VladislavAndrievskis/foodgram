import styles from './style.module.css'
import cn from 'classnames'
import { LinkComponent } from '../index'
import navigation from '../../configs/navigation'
import { UserMenu, NotLoggedInMenu } from '../../configs/navigation' // ✅ Импортируем дополнительные меню

const Nav = ({ loggedIn, orders }) => {
  // ✅ Объединяем основное меню с нужным дополнительным
  const navItems = loggedIn
    ? [...navigation, ...UserMenu]        // Если вошёл — добавляем UserMenu
    : [...navigation, ...NotLoggedInMenu] // Если не вошёл — добавляем NotLoggedInMenu

  return (
    <nav className={styles.nav}>
      <div className={styles.nav__container}>
        <ul className={styles.nav__items}>
          {navItems.map(item => (
            <li
              className={cn(styles.nav__item, {
                [styles.nav__item_active]: false,
              })}
              key={item.href}
            >
              <LinkComponent
                title={item.title}
                activeClassName={styles.nav__link_active}
                href={item.href}
                exact
                className={styles.nav__link}
              />
              {/* Счётчик заказов только для корзины */}
              {item.href === '/cart' && orders > 0 && (
                <span className={styles['orders-count']}>{orders}</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </nav>
  )
}

export default Nav

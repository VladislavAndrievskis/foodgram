const AccountMenuMobile = ({ onSignOut, orders }) => {
    const authContext = useContext(AuthContext);
    const location = useLocation();
    if (!authContext) {
        return (
            <div className={styles.menu}>
                {NotLoggedInMenu.map(item => {
                    return location.pathname === item.href ? (
                        <Button
                            key={item.href} // ✅ Добавлен ключ
                            href={item.href}
                            modifier="style_dark"
                            className={styles.menuButton}
                        >
                            {item.title}
                        </Button>
                    ) : (
                        <LinkComponent
                            key={item.href} // ✅ Добавлен ключ
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
            <AccountMobile onSignOut={onSignOut} orders={orders} />
        </div>
    );
};

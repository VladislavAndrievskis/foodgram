import { useEffect } from 'react';
import api from '../../api';
import {
    Button,
    Container,
    Main,
    PurchaseList,
    Title,
} from '../../components';
import { useRecipes } from '../../utils/index.js';
import styles from './styles.module.css';

const Cart = ({ updateOrders, orders }) => {
    const { recipes, setRecipes, handleAddToCart } = useRecipes();

    const getRecipes = () => {
        api.getRecipes({
            page: 1,
            limit: 999,
            is_in_shopping_cart: Number(true),
        }).then(res => {
            const { results } = res;
            setRecipes(results);
        });
    };

    useEffect(_ => {
        getRecipes();
    }, []);

    const downloadDocument = () => {
        api.downloadFile();
    };

    return (
        <Main>
            <Container className={styles.container}>
                <Helmet>
                    <title>Список покупок</title>
                    <meta
                        name="description"
                        content="Фудграм - Список покупок"
                    />
                    <meta property="og:title" content="Список покупок" />
                </Helmet>
                <div className={styles.cart}>
                    <Title title="Список покупок" />
                    <PurchaseList
                        orders={recipes}
                        handleRemoveFromCart={handleAddToCart}
                        updateOrders={updateOrders}
                    />
                    {orders > 0 && (
                        <Button
                            modifier="style_dark"
                            clickHandler={downloadDocument}
                        >
                            Скачать список
                        </Button>
                    )}
                </div>
            </Container>
        </Main>
    );
};

export default Cart;

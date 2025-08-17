import { Helmet } from 'react-helmet-async';
import { useEffect } from 'react';
import api from '../../api';
import {
    Container,
    Main,
    Pagination,
    SubscriptionList,
    Title,
} from '../../components';
import { useSubscriptions } from '../../utils';

const SubscriptionsPage = () => {
    const {
        subscriptions,
        setSubscriptions,
        subscriptionsCount,
        setSubscriptionsCount,
        removeSubscription,
        subscriptionsPage,
        setSubscriptionsPage,
    } = useSubscriptions();

    const getSubscriptions = ({ page }) => {
        api.getSubscriptions({ page }).then(res => {
            setSubscriptions(res.results);
            setSubscriptionsCount(res.count);
        });
    };

    useEffect(
        _ => {
            getSubscriptions({ page: subscriptionsPage });
        },
        [subscriptionsPage]
    );

    return (
        <Main>
            <Container>
                <Helmet>
                    <title>Мои подписки</title>
                    <meta
                        name="description"
                        content="Фудграм - Мои подписки"
                    />
                    <meta property="og:title" content="Мои подписки" />
                </Helmet>
                <Title title="Мои подписки" />
                <SubscriptionList
                    subscriptions={subscriptions}
                    removeSubscription={removeSubscription}
                />
                <Pagination
                    count={subscriptionsCount}
                    limit={6}
                    onPageChange={page => {
                        setSubscriptionsPage(page);
                    }}
                />
            </Container>
        </Main>
    );
};

export default SubscriptionsPage;

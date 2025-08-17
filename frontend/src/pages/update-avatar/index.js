import { useContext, useState } from 'react';
import {
    Button,
    Container,
    FileInput,
    Form,
    FormTitle,
    Main,
} from '../../components';
import { UserContext } from '../../contexts';
import styles from './styles.module.css';

const UpdateAvatar = ({ onAvatarChange }) => {
    const userContext = useContext(UserContext);

    const [avatarFile, setAvatarFile] = useState(userContext.avatar || null);
    const [updated, setUpdated] = useState(false);

    const checkIfDisabled = () => {
        return avatarFile === '' || avatarFile === null || !updated;
    };

    return (
        <Main withBG asFlex>
            <Container className={styles.center}>
                <Helmet>
                    <title>Регистрация</title>
                    <meta
                        name="description"
                        content="Фудграм - Редактирование аватара"
                    />
                    <meta
                        property="og:title"
                        content="Редактирование аватара"
                    />
                </Helmet>
                <Form
                    className={styles.form}
                    onSubmit={e => {
                        e.preventDefault();
                        if (checkIfDisabled()) {
                            return alert('Аватар не выбран или не заменен');
                        }
                        onAvatarChange({ file: avatarFile });
                    }}
                >
                    <FormTitle>Аватар</FormTitle>
                    <FileInput
                        onChange={file => {
                            setUpdated(true);
                            setAvatarFile(file);
                        }}
                        fileTypes={['image/png', 'image/jpeg']}
                        fileSize={5000}
                        className={styles.fileInput}
                        file={avatarFile}
                    />
                    <Button
                        modifier="style_dark"
                        type="submit"
                        className={styles.button}
                    >
                        Обновить аватар
                    </Button>
                </Form>
            </Container>
        </Main>
    );
};

export default UpdateAvatar;

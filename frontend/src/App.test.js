// src/App.test.js
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

test('renders main page', () => {
    render(
        <MemoryRouter initialEntries={['/']}>
            <App />
        </MemoryRouter>
    );

    // Проверяем, что на главной есть какой-то текст
    expect(screen.getByText(/рецепты/i)).toBeInTheDocument();
});

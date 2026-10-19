import React from 'react'
import './../../static/tailwindcss/input.css'
import { createRoot } from 'react-dom/client';
import { Contact } from '../components/contact';

const customer_management_container = document.getElementById("contact");
createRoot(customer_management_container).render(
    <React.StrictMode>
        <Contact />
    </React.StrictMode>
)
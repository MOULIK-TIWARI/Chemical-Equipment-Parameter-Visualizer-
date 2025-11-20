# Chemical Equipment Analytics - React Frontend

This is the React web frontend for the Chemical Equipment Analytics application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
src/
├── components/
│   ├── Auth/           # Authentication components
│   ├── Upload/         # File upload components
│   ├── Dashboard/      # Dashboard and data visualization
│   ├── History/        # Dataset history components
│   └── Reports/        # PDF report components
├── services/
│   └── api.js          # API service layer
├── utils/
│   └── auth.js         # Authentication utilities
├── App.jsx             # Main application component
└── main.jsx            # Application entry point
```

## Technologies

- React 18.x
- Vite (build tool)
- Axios (HTTP client)
- Chart.js & react-chartjs-2 (data visualization)
- React Router (routing)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

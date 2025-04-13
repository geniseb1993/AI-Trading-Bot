import '../styles/globals.css';
import { NotificationProvider } from '../contexts/NotificationContext';
import Layout from '../components/Layout';

function MyApp({ Component, pageProps }) {
  return (
    <NotificationProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </NotificationProvider>
  );
}

export default MyApp; 
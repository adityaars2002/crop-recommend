import { lazy, Suspense } from 'react';
import { createBrowserRouter } from 'react-router-dom';
import { Layout } from '../components/layout';
import { Loader } from '../components/ui';

// Lazy-loaded pages for code splitting
const HomePage = lazy(() => import('../pages/Home/HomePage'));
const CropRecommendationPage = lazy(() => import('../pages/CropRecommendation/CropRecommendationPage'));
const DiseaseDetectionPage = lazy(() => import('../pages/DiseaseDetection/DiseaseDetectionPage'));
const CropsPage = lazy(() => import('../pages/Crops/CropsPage'));
const CropDetailsPage = lazy(() => import('../pages/CropDetails/CropDetailsPage'));
const HistoryPage = lazy(() => import('../pages/History/HistoryPage'));
const NotFoundPage = lazy(() => import('../pages/NotFound/NotFoundPage'));

function SuspenseWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<Loader message="Loading page..." />}>
      {children}
    </Suspense>
  );
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <SuspenseWrapper><HomePage /></SuspenseWrapper>,
      },
      {
        path: 'crop-recommendation',
        element: <SuspenseWrapper><CropRecommendationPage /></SuspenseWrapper>,
      },
      {
        path: 'disease-detection',
        element: <SuspenseWrapper><DiseaseDetectionPage /></SuspenseWrapper>,
      },
      {
        path: 'crops',
        element: <SuspenseWrapper><CropsPage /></SuspenseWrapper>,
      },
      {
        path: 'crops/:id',
        element: <SuspenseWrapper><CropDetailsPage /></SuspenseWrapper>,
      },
      {
        path: 'history',
        element: <SuspenseWrapper><HistoryPage /></SuspenseWrapper>,
      },
      {
        path: '*',
        element: <SuspenseWrapper><NotFoundPage /></SuspenseWrapper>,
      },
    ],
  },
]);

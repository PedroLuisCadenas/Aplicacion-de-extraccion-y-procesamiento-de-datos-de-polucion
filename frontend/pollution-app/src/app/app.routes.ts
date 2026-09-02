// Tabla de rutas de la aplicación Angular

import { Routes } from '@angular/router';
import { Dashboard } from './features/dashboard/dashboard';
import { SensorsReadings } from './features/sensors-readings/sensors-readings';
import { Charts } from './features/charts/charts';
import { Informacion } from './features/informacion/informacion';

export const routes: Routes = [
  { path: '', component: Dashboard }, // ruta de inicio
  { path: 'sensors-readings', component: SensorsReadings },
  { path: 'charts', component: Charts },
  { path: 'informacion', component: Informacion }
];

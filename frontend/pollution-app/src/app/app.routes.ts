import { Routes } from '@angular/router';
import { Dashboard } from './features/dashboard/dashboard';
import { SensorsReadings } from './features/sensors-readings/sensors-readings';

export const routes: Routes = [
  { path: '', component: Dashboard },
  { path: 'sensors-readings', component: SensorsReadings }
];

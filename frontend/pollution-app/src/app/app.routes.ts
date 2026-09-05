// Tabla de rutas de la aplicación Angular

import { Routes } from '@angular/router';
import { Dashboard } from './features/dashboard/dashboard';
import { SensorsReadings } from './features/sensors-readings/sensors-readings';
import { Charts } from './features/charts/charts';
import { Dispositivo } from './features/dispositivo/dispositivo';
import { Usuario } from './features/usuario/usuario';
import { Ayuda } from './features/ayuda/ayuda';

export const routes: Routes = [
  { path: '', component: Dashboard }, // ruta de inicio
  { path: 'sensors-readings', component: SensorsReadings },
  { path: 'charts', component: Charts },
  { path: 'dispositivo', component: Dispositivo },
  { path: 'usuario', component: Usuario },
  { path: 'ayuda', component: Ayuda },
];

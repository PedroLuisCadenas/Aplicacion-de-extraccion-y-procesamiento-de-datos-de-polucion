import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { Api, DeviceInfo, LatestReadings } from '../../core/api';

@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceInfo = signal<DeviceInfo | null>(null);
  protected readonly userInfo = signal<any | null>(null);
  protected readonly readings = signal<LatestReadings | null>(null);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly deviceInfoEntries = computed(() =>
    Object.entries(this.deviceInfo() ?? {}),
  );

  protected readonly userInfoEntries = computed(() =>
    Object.entries(this.userInfo() ?? {}),
  );

  protected readonly sensorEntries = computed(() =>
    Object.entries(this.readings() ?? {}).sort(([a], [b]) => a.localeCompare(b)),
  );

  ngOnInit(): void {
    this.api.getLatestDeviceInfo().subscribe({
      next: (info) => this.deviceInfo.set(info),
      error: () => this.error.set('No se ha podido cargar la información del dispositivo.'),
    });

    this.api.getLatestReadings().subscribe({
      next: (readings) => {
        this.readings.set(readings);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se han podido cargar las últimas lecturas.');
        this.loading.set(false);
      },
    });

    this.api.getUserInfo().subscribe({
      next: (info) => this.userInfo.set(info),
      error: () => {
        this.error.set('No se ha podido cargar la información del usuario.');
      },
    });
  }
}

import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, DeviceElement, DeviceInfo, LatestReadings } from '../../core/api';

const MAX_BACKFILL_DIAS = 60; // 2 meses

const DEVICE_INFO_FIELDS: Record<string, { label: string; unit?: string }> = {
  tag: { label: 'Tag' },
  serial_number: { label: 'Número de serie' },
  battery_level: { label: 'Nivel de batería', unit: '%' },
  rx_signal_level: { label: 'RSSI 4G', unit: 'dBm' },
};

function formatEntries(
  info: Record<string, unknown> | null,
  fields: Record<string, { label: string; unit?: string }>,
): [string, string][] {
  return Object.entries(info ?? {}).map(([key, value]) => {
    const field = fields[key];
    if (!field) {
      return [key, String(value)];
    }
    const formattedValue = field.unit ? `${value} ${field.unit}` : String(value);
    return [field.label, formattedValue];
  });
}

@Component({
  selector: 'app-dispositivo',
  imports: [FormsModule],
  templateUrl: './dispositivo.html',
  styleUrl: './dispositivo.css',
})
export class Dispositivo implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceInfo = signal<DeviceInfo | null>(null);
  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly latestReadings = signal<LatestReadings>({});
  protected readonly error = signal<string | null>(null);

  protected readonly backfillDias = signal<number>(14);
  protected readonly backfillMsg = signal<string | null>(null);
  protected readonly backfillLoading = signal(false);

  protected readonly deviceInfoEntries = computed(() =>
    formatEntries(this.deviceInfo(), DEVICE_INFO_FIELDS),
  );

  // Temperatura interna del dispositivo (distinta de la ambiental, que se muestra en Inicio).
  protected readonly internalTemp = computed(() => {
    const element = this.deviceElements().find((e) => e.id === 'Temp');
    const value = this.latestReadings()['Temp'];
    if (!element || value == null) {
      return null;
    }
    return { value, unit: element.unit };
  });

  lanzarBackfill(): void {
    const dias = this.backfillDias();
    if (!dias || dias < 1 || dias > MAX_BACKFILL_DIAS) {
      this.backfillMsg.set(`El número de días debe estar entre 1 y ${MAX_BACKFILL_DIAS} (2 meses).`);
      return;
    }

    this.backfillLoading.set(true);
    this.backfillMsg.set(null);
    this.api.runBackfill(dias).subscribe({
      next: (res) => {
        this.backfillMsg.set(
          `Backfill de ${res.days} días iniciado. Puede tardar unos minutos; revisa las gráficas para ver los datos.`,
        );
        this.backfillLoading.set(false);
      },
      error: (err) => {
        this.backfillMsg.set(err?.error?.detail ?? 'No se ha podido lanzar el backfill.');
        this.backfillLoading.set(false);
      },
    });
  }

  ngOnInit(): void {
    this.api.getLatestDeviceInfo().subscribe({
      next: (info) => this.deviceInfo.set(info),
      error: () => this.error.set('No se ha podido cargar la información del dispositivo.'),
    });
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
    this.api.getLatestReadings().subscribe({
      next: (readings) => this.latestReadings.set(readings),
      error: () => this.error.set('No se han podido cargar las lecturas del dispositivo.'),
    });
  }
}

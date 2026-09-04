import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Api, DeviceElement, DeviceInfo } from '../../core/api';
import { SENSOR_DESCRIPTIONS } from '../../core/sensor-catalog';

const MAX_BACKFILL_DIAS = 60; // 2 meses

const DEVICE_INFO_FIELDS: Record<string, { label: string; unit?: string }> = {
  tag: { label: 'Tag' },
  serial_number: { label: 'Número de serie' },
  battery_level: { label: 'Nivel de batería', unit: '%' },
  rx_signal_level: { label: 'RSSI 4G', unit: 'dBm' },
};

const USER_INFO_FIELDS: Record<string, { label: string; unit?: string }> = {
  account_profile: { label: 'Tipo de perfil' },
  account_type: { label: 'Tipo de cuenta' },
  email: { label: 'Email' },
  level: { label: 'Nivel' },
  name: { label: 'Nombre' },
  surname: { label: 'Apellidos' },
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
  selector: 'app-informacion',
  imports: [FormsModule],
  templateUrl: './informacion.html',
  styleUrl: './informacion.css',
})
export class Informacion implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceInfo = signal<DeviceInfo | null>(null);
  protected readonly userInfo = signal<any | null>(null);
  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly error = signal<string | null>(null);
  protected readonly currentPage = signal(1);
  private readonly PAGE_SIZE = 10;

  protected readonly backfillDias = signal<number>(14);
  protected readonly backfillMsg = signal<string | null>(null);
  protected readonly backfillLoading = signal(false);

  protected readonly deviceInfoEntries = computed(() =>
    formatEntries(this.deviceInfo(), DEVICE_INFO_FIELDS),
  );

  protected readonly userInfoEntries = computed(() =>
    formatEntries(this.userInfo(), USER_INFO_FIELDS),
  );

  protected readonly sensorCatalog = computed(() => {
    const elements = this.deviceElements();
    return elements.map((element) => ({
      id: element.id,
      name: element.name,
      unit: element.unit,
      description: SENSOR_DESCRIPTIONS[element.id] ?? 'Descripción no disponible',
    }));
  });

  protected readonly paginatedSensorCatalog = computed(() => {
    const startIndex = (this.currentPage() - 1) * this.PAGE_SIZE;
    return this.sensorCatalog().slice(startIndex, startIndex + this.PAGE_SIZE);
  });

  protected readonly totalPages = computed(() => {
    return Math.ceil(this.sensorCatalog().length / this.PAGE_SIZE);
  });

  protected readonly pageRangeStart = computed(() => {
    if (this.sensorCatalog().length === 0) {
      return 0;
    }
    return (this.currentPage() - 1) * this.PAGE_SIZE + 1;
  });

  protected readonly pageRangeEnd = computed(() => {
    return Math.min(this.currentPage() * this.PAGE_SIZE, this.sensorCatalog().length);
  });

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

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
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
    this.api.getLatestDeviceInfo().subscribe({
      next: (info) => this.deviceInfo.set(info),
      error: () => this.error.set('No se ha podido cargar la información del dispositivo.'),
    });

    this.api.getUserInfo().subscribe({
      next: (info) => this.userInfo.set(info),
      error: () => {
        this.error.set('No se ha podido cargar la información del usuario.');
      },
    });
  }
}

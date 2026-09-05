import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { Api } from '../../core/api';

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
  selector: 'app-usuario',
  imports: [],
  templateUrl: './usuario.html',
  styleUrl: './usuario.css',
})
export class Usuario implements OnInit {
  private readonly api = inject(Api);

  protected readonly userInfo = signal<any | null>(null);
  protected readonly error = signal<string | null>(null);

  protected readonly userInfoEntries = computed(() =>
    formatEntries(this.userInfo(), USER_INFO_FIELDS),
  );

  ngOnInit(): void {
    this.api.getUserInfo().subscribe({
      next: (info) => this.userInfo.set(info),
      error: () => this.error.set('No se ha podido cargar la información del usuario.'),
    });
  }
}

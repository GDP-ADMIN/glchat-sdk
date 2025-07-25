import type { UploadedFile } from '../types';
import { PipelineFileSchema } from './types';

export class PipelineAPI {
  public constructor(private readonly client: typeof fetch) {}

  public async register(plugin: UploadedFile) {
    PipelineFileSchema.parse(plugin);

    const form = new FormData();

    form.append(
      'files',
      plugin,
      plugin.name ?? 'plugin.zip',
    );

    const response = await this.client('register-pipeline-plugin', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: form,
    });

    return response.json();
  }

  public async unregister(pluginId: string[]) {

  };
}

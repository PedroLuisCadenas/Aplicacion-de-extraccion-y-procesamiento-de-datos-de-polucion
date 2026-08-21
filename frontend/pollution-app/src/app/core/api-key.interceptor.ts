import { environment } from '../../environments/environment';
import { HttpInterceptorFn } from '@angular/common/http';

export const apiKeyInterceptor: HttpInterceptorFn = (req, next) => {
    const apiKey = environment.apiKey;
    if (req.url.includes('/api/v1/')) {
        const modifiedReq = req.clone({
            setHeaders: {
                'x-api-key': apiKey,
            }
        });
        return next(modifiedReq);
    }
    return next(req);
}

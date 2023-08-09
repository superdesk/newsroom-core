
export const INIT_DASHBOARD = 'INIT_DASHBOARD';
export function initDashboard(dashboards: any) {
    return {type: INIT_DASHBOARD, dashboards: dashboards};
}

export const SELECT_DASHBOARD = 'SELECT_DASHBOARD';
export function selectDashboard(dashboard: any) {
    return {type: SELECT_DASHBOARD, dashboard: dashboard};
}

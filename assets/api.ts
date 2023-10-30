import {IArticle} from './interfaces';
import {gettext} from './utils';

export interface INewshubApi {
    ui: {
        wire: {
            getVersionsLabelText(item: IArticle, plural?: boolean): string;
        };
    };
    localization: {
        gettext(message: string, params?: {[key: string]: string | number}): string;
    };
}

function getVersionsLabelText(_item: IArticle, plural?: boolean): string {
    return plural === true ?
        gettext('version') :
        gettext('versions');
}

export const newshubApi: INewshubApi = {
    ui: {wire: {getVersionsLabelText: getVersionsLabelText}},
    localization: {gettext: gettext},
};

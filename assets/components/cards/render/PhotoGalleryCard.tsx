import React from 'react';
import MoreNewsButton from './MoreNewsButton';
import {IProps4PhotoGallery} from '../utils';

const getMediaPanel = (photo: any, index: any) => {
    return (<div key={index} className='col-sm-6 col-lg-3 d-flex mb-4'>
        <div className='card card--home card--gallery'
            onClick={()=>{window.open(photo.href,'_blank');}}>
            <img className='card-img-top' src={photo.media_url} alt={photo.description} />
            <div className='card-body'>
                <h4 className='card-title'>{photo.description}</h4>
            </div>
        </div>
    </div>);
};

const PhotoGalleryCard: React.ComponentType<IProps4PhotoGallery> = (props: IProps4PhotoGallery) => {
    const {photos, title, moreUrl, moreUrlLabel} = props;

    return (
        <div className='row'>
            <MoreNewsButton kind="product" key="more" title={title} photoUrl={moreUrl} photoUrlLabel={moreUrlLabel} />
            {photos.map((photo: any, index: any) => getMediaPanel(photo, index))}
        </div>
    );
};

export default PhotoGalleryCard;

import pandas as pd
from scipy.stats import gamma, halfnorm, uniform

from astro_prost.associate import associate_sample, prepare_catalog
from astro_prost.helpers import SnRateAbsmag
from astropy.coordinates import SkyCoord
import importlib.resources as pkg_resources
import astropy.units as u
import time

def associate_glade():
        pkg = pkg_resources.files("astro_prost")
        pkg_data_file = pkg / "data" / "ZTFBTS_TransientTable.csv"
        with pkg_resources.as_file(pkg_data_file) as csvfile:
            transient_catalog = pd.read_csv(csvfile)
        transient_catalog = transient_catalog.sample(n=5)

	# define priors for properties
	priorfunc_z = halfnorm(loc=0.0001, scale=0.5)
	priorfunc_offset = uniform(loc=0, scale=10)
	priorfunc_absmag = uniform(loc=-30, scale=20)

	likefunc_offset = gamma(a=0.75)
	likefunc_absmag = SnRateAbsmag(a=-30, b=-10)

	priors = {"offset": priorfunc_offset, "absmag": priorfunc_absmag, "z": priorfunc_z}
	likes = {"offset": likefunc_offset, "absmag": likefunc_absmag}

	# set up properties of the association run
	verbose = 1
	save = False
	progress_bar = False
	cat_cols = False

	# list of catalogs to search -- options are (in order) glade, decals, panstarrs
	catalogs = ["glade"]

	# the name of the coord columns in the dataframe
	transient_coord_cols = ("RA", "Dec")

	# the column containing the transient names
	transient_name_col = "IAUID"

	transient_catalog = prepare_catalog(
	    transient_catalog, transient_name_col=transient_name_col, transient_coord_cols=transient_coord_cols
	)

	# cosmology can be specified, else flat lambdaCDM is assumed with H0=70, Om0=0.3, Ode0=0.7
        start_serial = time.time()
	hostTable = associate_sample(
	    transient_catalog,
	    priors=priors,
	    likes=likes,
	    catalogs=catalogs,
	    parallel=False,
	    verbose=verbose,
	    save=save,
	    progress_bar=progress_bar,
	    cat_cols=cat_cols,
	)
        end_serial = time.time()

        # cosmology can be specified, else flat lambdaCDM is assumed with H0=70, Om0=0.3, Ode0=0.7
        start_parallel = time.time()
        hostTable = associate_sample(
            transient_catalog,
            priors=priors,
            likes=likes,
            catalogs=catalogs,
            parallel=True,
            verbose=verbose,
            save=save,
            progress_bar=progress_bar,
            cat_cols=cat_cols,
        )
        end_parallel = time.time()

        duration_serial = end_serial - start_serial
        duration_parallel = end_parallel - start_parallel 
        assert duration_parallel < duration_serial